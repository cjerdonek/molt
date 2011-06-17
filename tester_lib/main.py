#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (C) 2011 Chris Jerdonek. All rights reserved.
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
Runs all unit tests and doc tests in the project.

"""

import doctest
import glob
import logging
import os
import sys
import unittest


_log = logging.getLogger(__name__)

LIBRARY_PACKAGE_NAME = 'molt_lib'
README_PATH = os.path.join(os.pardir, 'README.md')
TEST_MODULE_PATTERN = '*_unittest.py'


# TODO: run the doc tests in all modules.
def run_doc_tests():
    """Run the doc tests, and return (failure_count, test_count)."""
    result = doctest.testfile(README_PATH)

    return result


class DocTestsTestCase(unittest.TestCase):

    """
    A unittest TestCase that runs the doc tests.

    We wrap the doc tests inside a TestCase so that the aggregate unittest
    test run will reflect the success or failure of the doc tests.
    In particular, the success or failure of the doc tests will be reflected
    in the exit status.

    """

    def setUp(self):
        # TODO: Find a better way to move to the start of the next line.
        print
        _log.info("Running all doc tests as a single unit test...")

    # The name "runTest" is a magic value.
    def runTest(self):
        (failure_count, test_count) = run_doc_tests()
        if failure_count is 0:
            return

        msg = "%s out of %s doc tests failed." % (failure_count, test_count)
        # We log the error before calling the assertion.  Otherwise, the
        # message will not be logged on assertion failure.
        _log.error(msg)
        self.assertEquals(failure_count, 0, msg)


def create_doc_tests_suite(suite_class):
    """
    Return a TestSuite that runs the doc tests.

    """
    test_case = DocTestsTestCase()  # methodName parameter defaults to "runTest".
    test_cases = [test_case]
    test_suite = suite_class(tests=test_cases)

    return test_suite


class TestLoader(unittest.TestLoader):

    """
    This TestLoader differs from unittest's default TestLoader by
    providing additional diagnostic information when an AttributeError
    occurs while loading a module.

    Because of Python issue 7559:

      http://bugs.python.org/issue7559#

    module ImportErrors are masked, along with the name of the offending
    module.  This TestLoader reports the name of the offending module
    along with a reminder that the AttributeError may be masking an
    ImportError.

    """

    def loadTestsFromNames(self, names, module=None):
        """
        Return a suite of all doc tests and test cases in the package.

        """
        suites = []

        for name in names:
            try:
                suite = self.loadTestsFromName(name, module)
            except AttributeError as err:
                msg = """\

ERROR: AttributeError while loading unit tests from--
    %s
  Note that due to a bug in Python's unittest module, the AttributeError may
  be masking an ImportError in the module being processed.

""" % repr(name)
                # TODO: switch to using the logger.
                sys.stderr.write(msg)
                raise
            suites.append(suite)

        # We put the doc tests suite at the end rather than the beginning
        # because this makes it easier to log a message marking the
        # transition from the usual style unit tests to the doc tests.
        # For example, a message logged in the tearDown() of the doc tests
        # test case will display before the information on any doc test
        # failures, which is not what we want.
        doc_tests_suite = create_doc_tests_suite(self.suiteClass)
        suites.append(doc_tests_suite)

        return self.suiteClass(suites)


# TODO: move this function to the top of the module.
# TODO: This method should accept a logging level to permit verbose
# logging while running the tests.
# TODO: finish documenting this method.
def configure_test_logging():
    """
    Configure logging for this script.

    Configures a "black hole" log handler for the root logger to prevent the
    following message from being written while running tests:

      'No handlers could be found for logger...'

    It also prevents the handler from displaying any log messages by
    configuring it to write to os.devnull instead of sys.stderr.

    """
    # Configure the root logger.
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    stream = open(os.devnull,"w")
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)

    # Configure this module's logger.
    logger = _log

    stream = sys.stderr
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _log.debug("Debug logging enabled.")


def path_to_module_name(path):
    """
    Convert a file path to a dotted module name, and return the name.

    This function assumes that the first directory in the file path
    is the first module name in the dotted module name.  In other words,
    the given path must be relative to the top-level directory in the
    package hierarchy.

    """
    root, ext = os.path.splitext(path)
    module_parts = []
    while True:
        root, tail = os.path.split(root)
        module_parts.append(tail)
        if not root:
            break
    module_parts.reverse()

    return ".".join(module_parts)


def find_matching_module_paths(top_dir, pattern):
    """
    Return the paths to the modules whose file names match the pattern.

    The function searches the given directory recursively.  The pattern
    should be a string that is a file globbing pattern suitable for
    passing to Python's glob module, for example "*_unittest.py".
    
    Returns:

    This function returns a list of relative paths.  The paths are relative
    to the given directory.  For example, if "./shapes/circle_unittest.py"
    relative to the given directory matches, then the function will return
    "shapes/circle_unittest.py" for that module.

    """
    original_dir = os.getcwd()

    try:
        # Temporarily switch directories as an easy way to generate paths
        # relative to the top directory.
        os.chdir(top_dir)

        paths = []
        for dir_path, dir_names, file_names in os.walk(os.curdir):
            glob_path = os.path.join(dir_path, pattern)
            for path in glob.glob(glob_path):
                # Remove the leading current directory portion (for example "./").
                path = os.path.normpath(path)
                paths.append(path)
    finally:
        os.chdir(original_dir)

    return paths


def find_unit_test_module_names(top_dir, filename_pattern, module_name):
    """
    Return the names of the modules whose file names match the pattern.

    """
    paths = find_matching_module_paths(top_dir, filename_pattern)
    names = [path_to_module_name(path) for path in paths]
    names = [".".join([module_name, name]) for name in names]
    return names


def run_unit_tests(top_dir, unittest_module_pattern, module_name):
    """Run the unit tests in the given directory."""
    # Test discovery was not added to unittest until Python 2.7:
    #
    #   http://docs.python.org/library/unittest.html#test-discovery
    #
    # We use our own test discovery method here to support test discovery
    # in Python 2.6 and earlier.
    module_names = find_unit_test_module_names(top_dir, unittest_module_pattern, module_name)

    # unittest.TestLoader's constructor, which is called directly by
    # unittest.main(), does not permit the defaultTest parameter to be
    # a list of test names -- only one name.  So we pass the test names
    # instead using the argv parameter.
    argv = [''] + module_names

    _log.info("Running unit tests...")
    unittest.main(testLoader=TestLoader(), module=None, argv=argv)


def main(sys_argv):
    """Run all unit tests."""
    configure_test_logging()
    _log.info("TEST....")

    module_dir = os.path.dirname(__file__)

    top_dir = os.path.join(module_dir, os.pardir, LIBRARY_PACKAGE_NAME)
    run_unit_tests(top_dir, TEST_MODULE_PATTERN, LIBRARY_PACKAGE_NAME)

