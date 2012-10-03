#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
replmv
======

Replace parts of file/directory names (e.g. to fix wrong non-ASCII characters)
and rename (move) the files/dirs accordingly.

This script is intended to be run on POSIX filesystems, that have BYTESTRING
file/directory names. It is NOT tested on / not intended for MS Windows.

replmv works by using a translation map that translates input bytestring
sequences to output bytestring sequences. Because of this, it can do very
flexible translations and is not limited to recoding character sets.

Thus, no matter how broken the names in your filesystem are, if you can define
a mapping (TRANS_TAB), replmv can fix the names for you.

BE CAREFUL:

* always use a utf-8 capable editor to edit this file
* always use dry_run = True first and READ the output, whether all
  renames (REN) are correct. Also look at the errors (ERR).
* only if completely sure, run with dry_run = False

Note: convmv (written in Perl) is a similar tool.
      Try both and use whatever works better for you.

:copyright: 2012 Thomas Waldmann <tw@waldmann-edv.de>
:license: MIT license
"""

dry_run = True  # True means: do not change anything in the filesystem

start_dir = '/home/nopublic'  # do NOT use unicode here!

# the usual non-ascii stuff that goes wrong (must be unicode):
GERMAN = u"äöüÄÖÜß"
FRENCH = u"âàéèêëçô"
SYMBOLS = u"©®°"

# SPECIAL is the stuff that this script processes by default
# Note: using less special characters can be better if you have a rather
# chaotic mix of codings in your filesystem
SPECIAL = GERMAN + FRENCH + SYMBOLS

# how it is (often: cp850 (DOS), iso-8859-1 (old Linux))
CODING_IN = "iso-8859-1"

# how it should be (usually your filesystem encoding, often: utf-8)
CODING_OUT = "utf-8"

verify_first = True  # True means to first verify if the name already
                     # decodes using CODING_OUT.
                     # NOTE: only makes sense for UTF codings, single-byte
                     # codings ALWAYS decode (but not always like you want)


def make_trans(chars, enc_in, enc_out):
    """
    make a translation table from a list (or string) of unicode characters,
    translating them from a enc_in encoded to a enc_out encoded bytestring.
    """
    assert isinstance(chars, unicode)
    return [(c.encode(enc_in), c.encode(enc_out)) for c in chars]


# TRANS_TAB is a list of tuples (input bytestrings, output bytestrings).
# The bytestrings may have length 1 or more (e.g. for multi-byte encodings
# or if you want to "asciify" non-ascii chars).
#
# Note: for special applications, build the tuple list manually (not using
# make_trans), this gives maximum flexibility!
TRANS_TAB = make_trans(SPECIAL, CODING_IN, CODING_OUT)


import os


def translate_string(s, trans_tab):
    """
    translate a bytestring using trans_tab,
    verify it is coding_out encoded afterwards.
    """
    for old, new in trans_tab:
        s = s.replace(old, new)
    return s


def verify_string(s, coding):
    """
    verify that s decodes using <coding> decoder
    (this only gives significant results for utf codings)
    """
    try:
        unicode(s, coding, 'strict')
        return True
    except UnicodeError:
        return False


def map_and_verify(s, trans_tab=TRANS_TAB, coding=CODING_OUT):
    """
    call mapstring on s, verify the result.
    if it is valid, use the mapped string, otherwise keep as is.
    """
    s_old = s
    s_new = translate_string(s, trans_tab)
    if verify_string(s_new, coding):
        return s_new
    else:
        print "ERR: %r did not verify" % s
        return s_old


def move(old, new):
    """
    rename a file/directory (except for dry_run), return the new name.of it.
    """
    if dry_run:
        return old
    try:
        if not os.path.exists(new): # better check, POSIX OS would overwrite
            os.rename(old, new)
            return new
        else:
            raise OSError # target already exists
    except OSError as err:
        print "ERR: %s - can not rename %s to %s" % (str(err), old, new)
        return old


def dirwalker(dirname, level=0, map_fn=lambda x: x, verbose=False):
    """
    recurse through directories, starting from dirname, rename files/dirs
    using map_fn.
    """
    if level > 100:
        raise "ERR: Too deeply nested directories (loop?)"
    if verbose and not dry_run and level < 3:
        print "DIR: %s" % dirname
    try:
        fnames = os.listdir(dirname)
    except OSError as err:
        print "ERR: %s" % str(err)
    else:
        for fname in fnames:
            if verify_first and verify_string(fname, CODING_OUT):
                new_fpath = os.path.join(dirname, fname)
            else:
                new_fname = map_fn(fname)
                fpath = os.path.join(dirname, fname)
                new_fpath = os.path.join(dirname, new_fname)
                if new_fname != fname:
                    if verbose and dry_run:
                        print "REN: %s -> %s" % (fpath, new_fpath)	    
                    new_fpath = move(fpath, new_fpath)
                    if verbose and not dry_run:
                        print "REN: %s" % new_fpath
            if os.path.isdir(new_fpath):
                dirwalker(new_fpath, level+1, map_fn, verbose)


if __name__ == '__main__':
    dirwalker(start_dir, map_fn=map_and_verify, verbose=True)

