#!/usr/bin/env python
# vim: set fileencoding=utf-8

import os
import io
import base64
import tarfile
tgbegin = '\n#==>\n#'.encode()
tgend   = '\n#<==\n'.encode()

def main():
    fname = __file__
    if fname.endswith('.pyc'):
        fname = fname[0:-1]

    content = open(fname, 'rb').read()
    s = content.find(tgbegin)
    e = content.find(tgend)
    body = content[0:s]
    
    tbz = content[s+len(tgbegin):e]
    tbz = base64.b64decode(tbz)
    tbz = io.BytesIO(tbz)
    with tarfile.open(fileobj=tbz) as t:
        t.extractall('tmp_')

    'gmock-1.7.0/fused-src/'

if __name__ == '__main__':
    main()
