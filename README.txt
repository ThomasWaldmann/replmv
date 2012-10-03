replmv
======

Replace parts of file/directory names (e.g. to fix wrong non-ASCII characters)
and rename (move) the files/dirs accordingly.

replmv is intended to be run on POSIX filesystems, that have BYTESTRING
file/directory names. It is NOT tested on / not intended for MS Windows.

replmv works by using a translation map that translates input bytestring
sequences to output bytestring sequences. Because of this, it can do very
flexible translations and is not limited to recoding character sets.

Thus, no matter how broken the names in your filesystem are, if you can define
a mapping (TRANS_TAB), replmv can fix the names for you.

Usage
-----
You just edit the parameters at the top of the script (read the comments)
before running the script. There are (intendedly) no commandline arguments.

BE CAREFUL:

* always use a utf-8 capable editor to edit replmv.py
* it still needs to be valid Python after your edit :)
* always use dry_run = True first and READ the output, whether all
  renames (REN) are correct. Also look at the errors (ERR).
* only if completely sure, run with dry_run = False

Note: replmv is written in Python.
      convmv (written in Perl) is a somehow similar tool.
      Try both and use whatever works better for you.

:copyright: 2012 Thomas Waldmann <tw@waldmann-edv.de>
:license: MIT license
