#!/usr/bin/env python
# vim: set fileencoding=utf-8

import os
import io
import re
import sys
import base64
import tarfile
from os import path
from pprint import pprint, pformat
from xml.etree import ElementTree

tgbegin = '\n#==>\n#'.encode()
tgend   = '\n#<==\n'.encode()

GMOCK_UNPACK_DIR = '.waf_unittest_gmock'

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
    extract_this(GMOCK_UNPACK_DIR)
    sys.exit(0)

from waflib.TaskGen import feature, before_method, after_method, taskgen_method
from waflib import Options, Logs, Errors, Utils, Task

testlock = Utils.threading.Lock()

def options(opt):
    opt.add_option('--notests',  action='store_true', default=False,
                   help='Exec no unit tests', dest='no_tests')
    opt.add_option('--alltests', action='store_true', default=False,
                   help='Exec all unit tests', dest='all_tests')
    opt.add_option('--testcmd', action='store', default=False,
                   help = ('Run the unit tests using the test-cmd string' +
                           ' example "--test-cmd="valgrind --error-exitcode=1' +
                           ' %s" to run under valgrind'), dest='testcmd')

def configure(conf):
    try:
        extract_this(GMOCK_UNPACK_DIR)
        conf.msg('Unpacking gmock', 'yes')
    except:
        conf.msg('Unpacking gmock', 'no')
        Logs.error(sys.exc_info()[1])


@feature('test')
@before_method('process_source')
def attach_gmock(self):
    if not getattr(self.bld, 'has_gmock_objects', False):
        self.bld(
            target = 'GMOCK_OBJECTS',
            features = 'cxx',
            source = [
                GMOCK_UNPACK_DIR + '/gmock-gtest-all.cc',
                GMOCK_UNPACK_DIR + '/gmock_main.cc',
            ],
            includes = [GMOCK_UNPACK_DIR],
            export_includes = [GMOCK_UNPACK_DIR],
        )
        self.bld.has_gmock_objects = True

    self.use = self.to_list(getattr(self, 'use', [])) + ['GMOCK_OBJECTS']

@feature('test')
@after_method('apply_link')
def make_test(self):
    """
    Create the unit test task. There can be only
    one unit test task by task generator.
    """
    if getattr(self, 'link_task', None):
        self.create_task('utest', self.link_task.outputs)

@taskgen_method
def add_test_results(self, tup):
    """
    Override and return tup[1] to interrupt the
    build immediately if a test does not run.
    """
    Logs.debug("ut: %r", tup)
    self.utest_result = tup
    try:
        self.bld.utest_results.append(tup)
    except AttributeError:
        self.bld.utest_results = [tup]

class utest(Task.Task):
    """
    Execute a unit test
    """
    color = 'PINK'
    after = ['vnum', 'inst']
    vars = []

    def runnable_status(self):
        """
        Always execute the task if `waf --alltests` was used or no
        tests if ``waf --notests`` was used
        """
        if getattr(Options.options, 'no_tests', False):
            return Task.SKIP_ME

        ret = super(utest, self).runnable_status()
        if ret == Task.SKIP_ME:
            if getattr(Options.options, 'all_tests', False):
                return Task.RUN_ME
        return ret

    def add_path(self, dct, path, var):
        dct[var] = os.pathsep.join(Utils.to_list(path) + [os.environ.get(var, '')])

    def get_test_env(self):
        """
        In general, tests may require any library built anywhere in the project.
        Override this method if fewer paths are needed
        """
        try:
            fu = getattr(self.generator.bld, 'all_test_paths')
        except AttributeError:
            # this operation may be performed by at most #maxjobs
            fu = os.environ.copy()

            lst = []
            for g in self.generator.bld.groups:
                for tg in g:
                    if getattr(tg, 'link_task', None):
                        s = tg.link_task.outputs[0].parent.abspath()
                        if s not in lst:
                            lst.append(s)

            if Utils.is_win32:
                self.add_path(fu, lst, 'PATH')
            elif Utils.unversioned_sys_platform() == 'darwin':
                self.add_path(fu, lst, 'DYLD_LIBRARY_PATH')
                self.add_path(fu, lst, 'LD_LIBRARY_PATH')
            else:
                self.add_path(fu, lst, 'LD_LIBRARY_PATH')
            self.generator.bld.all_test_paths = fu
        return fu

    def run(self):
        """
        Execute the test. The execution is always successful, and the results
        are stored on ``self.generator.bld.utest_results`` for postprocessing.

        Override ``add_test_results`` to interrupt the build
        """
        filename = self.inputs[0].abspath()
        output_filename = path.splitext(filename)[0]+'_result.xml'

        self.ut_exec = getattr(self.generator, 'ut_exec', [filename])
        self.ut_exec += ['--gtest_output=xml:{}'.format(output_filename)]
        if getattr(self.generator, 'ut_fun', None):
            self.generator.ut_fun(self)

        cwd = getattr(self.generator, 'ut_cwd', '') or self.inputs[0].parent.abspath()

        testcmd = getattr(self.generator, 'ut_cmd', False) or getattr(Options.options, 'testcmd', False)
        if testcmd:
            self.ut_exec = (testcmd % self.ut_exec[0]).split(' ')

        Logs.info(str(self.ut_exec))
        proc = Utils.subprocess.Popen(self.ut_exec, cwd=cwd, env=self.get_test_env(), stderr=Utils.subprocess.PIPE, stdout=Utils.subprocess.PIPE)
        (stdout, stderr) = proc.communicate()

        # read result from output_filename
        test_results = ElementTree.parse(output_filename).getroot()

        tup = (filename, proc.returncode, stdout, stderr, test_results)
        testlock.acquire()
        try:
            return self.generator.add_test_results(tup)
        finally:
            testlock.release()

def summary(bld):
    """
    Show the status of Google Test
    """
    lst = getattr(bld, 'utest_results', [])
    if not lst:
        return

    Logs.pprint('CYAN', '[test summary]')

    nfails = 0

    for (f, code, out, err, result) in lst:
        fail = int(result.attrib['failures'])
        if fail > 0:
            nfails += fail
            for failure in result.iter('failure'):
                message = failure.attrib['message']
                message_body = '\n'.join(message.split('\n')[1:])
                message = message.split('\n')[0]

                m = re.compile(r'^(.*):([0-9]+)$').match(message)
                body = m.group(1)
                num = int(m.group(2))
                Logs.error('{}({}): error: {}'.format(body, num, message_body))

    if nfails > 0:
        raise Errors.WafError('test failed')

def set_exit_code(bld):
    """
    If any of the tests fail waf will exit with that exit code.
    This is useful if you have an automated build system which need
    to report on errors from the tests.
    You may use it like this:

        def build(bld):
            bld(features='cxx cxxprogram test', source='main.c', target='app')
            from waflib.Tools import waf_unit_test
            bld.add_post_fun(waf_unit_test.set_exit_code)
    """
    lst = getattr(bld, 'utest_results', [])
    for (f, code, out, err, result) in lst:
        if code:
            msg = []
            if out:
                msg.append('stdout:%s%s' % (os.linesep, out.decode('utf-8')))
            if err:
                msg.append('stderr:%s%s' % (os.linesep, err.decode('utf-8')))
            bld.fatal(os.linesep.join(msg))
