#!/usr/bin/env python
# vim: set fileencoding=utf-8

import os
import io
import base64
import tarfile
tgbegin = '\n#==>\n#'.encode()
tgend   = '\n#<==\n'.encode()

def extract_this(dst):
    fname = __file__
    if fname.endswith('.pyc'):
        fname = fname[0:-1]

    # decode zipped files
    tbz = open(fname, 'rb').read()
    tbz = tbz[tbz.find(tgbegin) + len(tgbegin) : tbz.find(tgend)]
    tbz = base64.b64decode(tbz)
   
    # extract
    with tarfile.open(fileobj=io.BytesIO(tbz)) as t:
        t.extractall(dst)

if __name__ == '__main__':
    extract_this('tmp_')
