# encoding: utf-8
#
# Copyright (C) 2011-2012 Chris Jerdonek. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The names of the copyright holders may not be used to endorse or promote
#   products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
Exposes a generic run_tests() function to run all tests in a project.

"""

# TODO: unit test this module.

from __future__ import absolute_import

import doctest
import os
from pkgutil import walk_packages
import sys
from unittest import TestLoader, TestProgram, TextTestRunner

from molt.test.harness.common import test_logger as _log
from molt.test.harness.sandbox import TestConfig


def make_doctest_test_suites(module_names):
    """
    Return a list of TestSuite instances for the doctests in the given modules.

    """
    suites = []
    for module in module_names:
        try:
            suite = doctest.DocTestSuite(module)
        except ImportError, err:
            raise Exception("Error building doctests for %s:\n  %s: %s" %
                            (module, err.__class__.__name__, err))
        suites.append(suite)
    return suites


def make_doctest_file_suites(paths):
    """
    Return a list of TestSuite instances for the doctests in the given text files.

    """
    suites = []
    for path in paths:
        suite = doctest.DocFileSuite(path, module_relative=False)
        suites.append(suite)
    return suites


def make_doctests(module_names, text_paths):
    """
    Return a list of TestSuite instances containing all project doctests.

    """
    suites = make_doctest_test_suites(module_names)
    suites.extend(make_doctest_file_suites(text_paths))

    return suites


def find_modules(package):
    """
    Return a list of the names of modules inside a package.

    """
    dir_path = os.path.dirname(package.__file__)
    prefix = "%s." % package.__name__

    names = []
    for info in walk_packages(path=[dir_path], prefix=prefix):
        loader, name, ispkg = info
        names.append(name)

    return names


def run_tests(package, is_unittest_module, test_run_dir,
              extra_tests=None, doctest_paths=None, verbosity=1,
              test_runner_stream=None):
    """
    Run all tests, and return a unittest.TestResult instance.

    Arguments:

      verbosity: 0 for quiet, 1 for normal, 2 for verbose.  Defaults to 1.

      test_runner_stream: the stream object to pass to unittest.TextTestRunner.
        Defaults to sys.stderr.

    """
    if extra_tests is None:
        extra_tests = []
    if doctest_paths is None:
        doctest_paths = []
    if test_runner_stream is None:
        test_runner_stream = sys.stderr

    # TODO: consider using unittest's test discovery functionality
    #   added in Python 2.7.
    #
    # Test discovery was not added to unittest until Python 2.7:
    #
    #   http://docs.python.org/library/unittest.html#test-discovery
    #
    # We use our own test discovery method here to support test discovery
    # in Python 2.6 and earlier.
    module_names = find_modules(package)
    test_module_names = filter(is_unittest_module, module_names)

    doctests = make_doctests(module_names, doctest_paths)

    tests = extra_tests + doctests
    test_program_class = make_test_program_class(tests)

    argv = ['']

    # unittest.TestLoader's constructor, which is called directly by
    # unittest.main(), does not permit the defaultTest parameter to be
    # a list of test names -- only one name.  So we pass the test names
    # instead using the argv parameter.
    argv.extend(test_module_names)

    test_config = TestConfig(test_run_dir)

    test_loader = UnittestTestLoader()
    test_loader.test_config = test_config

    test_runner = TextTestRunner(stream=test_runner_stream, verbosity=verbosity)
    test_program = test_program_class(argv=argv, module=None, exit=False, verbosity=verbosity,
                                      testLoader=test_loader, testRunner=test_runner)

    return test_program.result


def make_test_program_class(tests):
    """
    Return a unittest.TestProgram subclass that adds a list of custom tests.

    Arguments:

      tests: an iterable of TestCase and TestSuite instances to add in
        addition to the usual tests loaded when calling createTests().

    """
    class PystacheTestProgram(TestProgram):

        """
        Instantiating an instance of this class runs all tests.

        For example, calling unittest.main() is an alias for calling the
        constructor unittest.TestProgram().

        The TestProgram constructor does the following:

        1. Calls self.parseArgs(argv),
        2. which in turn calls self.createTests().
        3. Then, the constructor calls self.runTests().

        """

        def createTests(self):
            """
            Load tests and set self.test to a unittest.TestSuite instance

            The base class's TestProgram.createTests() sets the self.test
            attribute by calling one of self.testLoader's "loadTests" methods.
            Each loadTest method returns a unittest.TestSuite instance.
            In particular, self.test is set to a TestSuite instance after
            calling the base class's createTests().

            """
            super(PystacheTestProgram, self).createTests()
            self.test.addTests(tests)

    return PystacheTestProgram


class UnittestTestLoader(TestLoader):

    """
    This TestLoader differs from unittest's default TestLoader by providing
    additional diagnostic information when an AttributeError occurs while
    loading a module.

    Because of Python issue 7559 ( http://bugs.python.org/issue7559# ),
    the unittest module masks ImportErrors and the name of the offending
    module.  This TestLoader reports the name of the offending module
    along with a reminder that the AttributeError may be masking an
    ImportError.

    """

    def loadTestsFromNames(self, names, module=None):
        """
        Return a suite of all unit tests and doctests in the package.

        """
        suites = []

        for name in names:
            try:
                suite = self.loadTestsFromName(name, module)
            except AttributeError as err:
                msg = """AttributeError while loading unit tests from:
%s

Due to a bug in Python's unittest module, the AttributeError may be masking
an ImportError in the module being processed.
""" % repr(name)
                # TODO: add to the existing exception instead of raising a new one.
                raise Exception(msg)
            suites.append(suite)

        return self.suiteClass(suites)

