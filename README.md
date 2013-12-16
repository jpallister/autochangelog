# Autochangelog: Automatically format changelog and git commits

This scipt will generate a ChangeLog entry based on the files to be committed.
The script will query about each file to be committed, asking for a message to
put in the ChangeLog/commit. This will be formatted and added to the ChangeLog
in the specified directory.

If this file is placed as a prepare-commit-msg hook in git
(.git/hooks/prepare-commit-msg), upon a normal commit (non merge, amend), a
commit message will be formed and prepopulated.

Example:
    james@computer% git commit
    Name: James Pallister
    Email: james.pallister@bristol.ac.uk

    There are 21 files staged for commit. Do you want to see a list? [y/N] y
       Makefile.in                    aclocal.m4
       analysis/Makefile.am           analysis/Makefile.in
       analysis/simulate.avr.in       configure
       configure.ac                   generate.avr
       src/2dfir/Makefile.in          src/blowfish/Makefile.in
       src/common.mk.am               src/crc32/Makefile.in
       src/cubic/Makefile.in          src/dijkstra/Makefile.in
       src/fdct/Makefile.in           src/float_matmult/Makefile.in
       src/int_matmult/Makefile.in    src/platformcode/Makefile.in
       src/rijndael/Makefile.in       src/sha/Makefile.in
       src/template/Makefile.in

    Enter a description of the changes:
     > Added detection of AVR simulator
    Enter a description of the changes for Makefile.in.
     > Regenerated
    Enter a description of the changes for aclocal.m4.
     > Regenerated
    Enter a description of the changes for analysis/Makefile.am.
     > Create simulate.avr
    ChangeLog entry generated, view, edit or continue [v/e/c] v
    2013-12-16  James Pallister  <james.pallister@bristol.ac.uk>
        Added detection of AVR simulator

        * Makefile.in: Regenerated
        * aclocal.m4: Regenerated
        * analysis/Makefile.am: Create simulate.avr

    [git commit editor opens]

## Requirements
* docopt
* colorama [optional]
