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
    """指定ディレクトリを圧縮したバイナリを取得する"""
    f = io.BytesIO() 
    with tarfile.open(fileobj=f, mode='w:bz2') as t:
        for root, dirs, files in os.walk(src):
            for _file in files:
                _file = os.path.join(root, _file)
                aname = os.path.relpath(_file, src)
                t.add(_file, arcname=aname)
    return f.getvalue()

def main():
    # read source files
    scr = open(TMPL_NAME, 'rb').read()
    tbz = to_tbz2(GMOCK_DIR)
   
    # append archived gmock files with signatures
    scr += tgbegin + base64.b64encode(tbz) + tgend

    # save
    with open(DEST_NAME, 'wb') as f:
        f.write(scr)

if __name__ == '__main__':
    main()
