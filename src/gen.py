#!/usr/bin/env python
# vim: set fileencoding=utf-8

import os
import sys
import tarfile
import base64

TMPL_NAME = 'waf_unittest_t.py'
DEST_NAME = 'waf_unittest_gmock.py'
GMOCK_DIR = 'gmock-1.7.0/fused-src'

tgbegin = '\n#==>\n#'.encode()
tgend   = '\n#<==\n'.encode()

import io

def to_tbz2(src):
    TBZ_NAME = 'fused_gmock.tar.bz2'
    with tarfile.open(TBZ_NAME, 'w:bz2') as t:
        for root, dirs, files in os.walk(src):
            for _file in files:
                _file = os.path.join(root, _file)
                aname = os.path.relpath(_file, src)
                t.add(_file, arcname=aname)
    with open(TBZ_NAME, 'rb') as f: 
        tbz = f.read()

    os.remove(TBZ_NAME)
    return tbz

def main():
    tbz = to_tbz2(GMOCK_DIR)
    
    scr = open(TMPL_NAME, 'rb').read()
    scr += tgbegin + base64.b64encode(tbz) + tgend

    with open(DEST_NAME, 'wb') as f:
        f.write(scr)

if __name__ == '__main__':
    main()
