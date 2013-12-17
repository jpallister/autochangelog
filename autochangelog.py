#!/usr/bin/python

#   Prepare commit message hook, to automatically add a ChangeLog entry
#   and prepare a commit message from that
#
#   Copyright (C) 2013 James Pallister
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Script to automatically create change log entries from staged files.

Usage:
    autochangelog.py [options] [COMMITFILE] [COMMITARGS...]

Options:
    --repo REPO         Directory of the repository [default: .]
    COMMITFILE          File to store commit message, doesn't save commit if
                        not specified

This scipt will generate a ChangeLog entry based on the files to be committed.
The script will query about each file to be committed, asking for a message to
put in the ChangeLog/commit. This will be formatted and added to the ChangeLog
in the specified directory.

This file should be sym-linked as both prepare-commit-msg and pre-commit, so 
ChangeLog can be added into the commit. Upon a normal commit (non merge, 
amend), a commit message will be formed and prepopulated.

"""
from docopt import docopt
import sys
print sys.argv
arguments = docopt(__doc__)

from subprocess import check_output, check_call
import os
import readline
import datetime
import string
import textwrap
from sys import stdout
import sys
import hashlib

try:
    from colorama import init, Fore
    init()
    blue = Fore.BLUE
    green = Fore.GREEN
    reset = Fore.RESET
except:
    print "Colorama python module not found... No colors"
    blue = ""
    green = ""
    reset = ""

def preinput(text):
    def f():
        stdout.write(blue)
        readline.insert_text(text)
        readline.redisplay()
    return f

def get_input(prompt, initial=""):
    readline.set_pre_input_hook(preinput(initial))
    inp = raw_input(prompt)
    stdout.write(reset)
    return inp

def choice(prompt, choices):
    sel = None

    while True:
        sel = get_input("{} [{}] ".format(prompt, "/".join(choices)))

        if sel == '':
            sel = None
            for c in choices:
                if c.isupper():
                    return c.lower()
        elif sel.lower() in map(string.lower, choices):
            return sel.lower()

def pre_commit():
    if len(arguments['COMMITARGS']) > 0: # Not a normal commit
        exit(0)

    # Get a list of cached files, plus our name and email
    os.chdir(arguments['--repo'])
    if not os.path.exists("ChangeLog"):
        print "Cannot find ChangeLog in", arguments['--repo']
        exit(1)

    staged_files = check_output("git diff --name-only --cached", shell=True).split()
    name = check_output("git config user.name", shell=True).strip()
    email = check_output("git config user.email", shell=True).strip()

    sys.stdin = open('/dev/tty')

    if "ChangeLog" in staged_files:
        print "ChangeLog already staged for commit."
        c = choice("Skip changelog+commit msg generation?", ["Y","n"])
        if c == "y":
            exit(0)

    name = get_input("Name: ", name)
    email = get_input("Email: ", email)

    print ""
    c = choice("There are {} files staged for commit. Do you want to see a list?".format(len(staged_files)), ["y", "N"])

    if c == 'y':
        # Pad names, so all strings are the same length
        maxlen = max(map(len, staged_files))
        padded = map(lambda x: x + " "*(maxlen-len(x)), staged_files)

        # Join the strings together, then text wrap and indent, to display nicely
        stdout.write(green)
        print "  ", '\n   '.join(textwrap.wrap(str("  ".join(padded)))), "\n"
        stdout.write(reset)

    date = datetime.date.today()
    entry = "{}  {}  <{}>\n".format(date, name, email)
    commit = ""

    msg = get_input("Enter a description of the changes:\n > ")
    if msg != "":
        # Text wrap message
        entry_msg = map(lambda x: "\t"+x+"\n", textwrap.wrap(msg, 70))
        commit_msg = map(lambda x: x+"\n", textwrap.wrap(msg, 72))

        entry += "".join(entry_msg)
        commit += "".join(commit_msg)
        commit += "\n"
    else:
        commit += "\n\n"  # We haven't got a message so leave it black (bad)
    entry += "\n"

    for f in staged_files:
        if f == "ChangeLog":
            continue
        elif os.path.basename(f) in ["Makefile.in", "configure", "aclocal.m4"]:
            initial = "Regenerated"
        else:
            initial = ""

        i = get_input("Enter a description of the changes for {}.\n > ".format(f), initial)

        if i == "":
            i = "-"

        emsg = textwrap.wrap(i, 66-len(f))
        cmsg = textwrap.wrap(i, 64-len(f))

        entry += "\t* {}: {}\n".format(f, emsg[0])
        commit += "    * {}: {}\n".format(f, cmsg[0])

        if len(msg) > 1:
            # Rewrap to larger line size
            emsg = textwrap.wrap(" ".join(emsg[1:]), 66)
            cmsg = textwrap.wrap(" ".join(cmsg[1:]), 64)

            # Indent lines
            emsg = map(lambda x: "\t    " + x + "\n", emsg)
            cmsg = map(lambda x: "        " + x + "\n", cmsg)

            entry += "".join(emsg)
            commit += "".join(cmsg)
    entry += "\n"

    c = None
    while c != "c":
        c = choice("ChangeLog entry generated, view, edit or continue".format(len(staged_files)), ["v", "e", "c"])

        if c == 'v':
            stdout.write(green)
            print entry
            stdout.write(reset)
        if c == "e":
            print "TODO"

    print "Added entry to ChangeLog"

    orig = open("ChangeLog", "r").read()

    f = open("ChangeLog", "w")
    f.write(entry + orig)
    f.close()

    check_output("git add ChangeLog", shell=True)

    md5 = hashlib.md5()
    md5.update(os.getcwd())
    f = open("/tmp/tmpcommit."+md5.hexdigest(),"w")
    f.write(commit)
    f.close()

def prepare_commit_msg():
    orig = open(arguments['COMMITFILE'], "r").read()

    md5 = hashlib.md5()
    md5.update(os.getcwd())
    if not os.path.exists("/tmp/tmpcommit."+md5.hexdigest()):
        commit = ""
    else:
        f = open("/tmp/tmpcommit."+md5.hexdigest(),"r")
        commit = f.read()
        f.close()

    f = open(arguments['COMMITFILE'], "w")
    f.write(commit + orig)
    f.close()

if __name__ == "__main__":
    if arguments['COMMITFILE'] is None:
        pre_commit()
    else:
        prepare_commit_msg()
