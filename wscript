#!/usr/bin/env python
# -*- coding: utf-8 -*-

TOP = '.'
OUT = 'build'

def options(opt):
    opt.load('compiler_cxx')
    opt.recurse('src')

def configure(conf):
    conf.load('compiler_cxx')
    conf.recurse('src')

    cxx_name = conf.env.CXX_NAME
    if cxx_name == 'msvc':
        conf.env.append_unique('CXXFLAGS', ['/EHsc'])
    elif cxx_name in ('g++', 'clang++'):
        conf.load('gnu_dirs')
        conf.check(lib='pthread')
        conf.env.append_unique('CXXFLAGS', ['-O2', '-Wall', '-std=c++11'])
        conf.env.append_unique('LIBS', ['PTHREAD'])
        if compiler == 'clang++':
            conf.env.append_unique('CXXFLAGS', ['-stdlib=libc++'])

def build(bld):
    bld.recurse('src')

    bld(features='cxx cxxprogram test',
        target = 'test_gtest',
        source = 'test_gtest.cc',
    )

    bld(features='cxx cxxprogram test',
        target = 'test_gmock',
        source = 'test_gmock.cc',
    )

