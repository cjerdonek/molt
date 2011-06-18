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

# TODO: unit test this module.

import doctest
import glob
import logging
from optparse import OptionParser
import os
import sys
import unittest


_log = logging.getLogger(__name__)

LIBRARY_PACKAGE_NAME = 'molt_lib'
README_PATH = os.path.join(os.pardir, 'README.md')
TEST_MODULE_PATTERN = '*_unittest.py'

USAGE = """%prog [options]

Runs the molt project's tests.

The project's tests include all of the unit tests and doctests in the
project.  This script uses Python's unittest and doctest modules to find
and run the tests.

Doctests, as described more fully in Python's doctest module, are example
interactive code snippets that show up in project documenation.  This
script looks for doctests in essentially all project files, for example
in the project's README file and in all of the Python code's docstrings.
A doctest might look like this:

>>> 1 + 1
2

For reporting reasons, this script runs all tests as unit tests.
In particular, the script runs all doctests collectively as a single
unit test.  In fact, they are the final unit test.  If any doctests fail,
the script reports the number of doctest failures separately in both
the script's output log messages and in the message text of the
corresponding unit test's AssertionError."""


# TODO: finish documenting this method.
def configure_logging(logging_level):
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

    logger.setLevel(logging_level)

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


def add_scanf_options(parser):
    """Add command-line options to the given OptionParser."""
    parser.add_option("-v", "--verbose", action='store_true', default=False,
                      help="log verbose output")


def should_log_verbosely(sys_argv):
    """
    Return whether verbose logging should be enabled.

    This function should never raise an Exception because it is meant
    to be called before logging is configured (in particular, before
    exception logging).

    """
    # The OptionParser we construct here is a dummy parser solely for
    # detecting the verbose logging option prior to configuring logging.
    # We disable the help option to prevent exiting when a help option
    # is passed (e.g. "-h" or "--help").
    parser = TesterOptionParser(add_help_option=False)
    add_scanf_options(parser)

    try:
        # The optparse module's parse_args() normally expects sys.argv[1:].
        (options, args) = parser.parse_args(sys_argv[1:])
    except UsageError:
        # Default to normal logging on error.  Any usage error will
        # occur again during the second pars.
        return False

    return options.verbose


def parse_args(sys_argv, usage=USAGE):
    """
    Parse the command arguments, and return (options, args).

    This function may call exit() for some arguments (e.g. "--version" or
    "--help").

    Raises:
    scanf.Error: if an error occurs while parsing.

    """
    parser = TesterOptionParser(usage)
    add_scanf_options(parser)

    # The optparse module's parse_args() normally expects sys.argv[1:].
    (options, args) = parser.parse_args(sys_argv[1:])

    return (options, args)


# TODO: run the doc tests in all modules.
def run_doc_tests(verbose=False):
    """Run the doc tests, and return (failure_count, test_count)."""
    result = doctest.testfile(README_PATH, verbose=verbose)

    return result


def create_doc_tests_suite(suite_class, verbose=False):
    """
    Return a TestSuite that runs the doc tests.

    """
    test_case = DocTestsTestCase(verbose=verbose)  # methodName parameter defaults to "runTest".
    test_cases = [test_case]
    test_suite = suite_class(tests=test_cases)

    return test_suite


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


def run_unit_tests(top_dir, unittest_module_pattern, module_name, verbose=False):
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
    test_loader = TestLoader(verbose=verbose)
    unittest.main(testLoader=test_loader, module=None, argv=argv)


def process_args(sys_argv):
    """Run all unit tests."""

    (options, args) = parse_args(sys_argv)

    verbose = options.verbose

    module_dir = os.path.dirname(__file__)

    top_dir = os.path.join(module_dir, os.pardir, LIBRARY_PACKAGE_NAME)
    run_unit_tests(top_dir, TEST_MODULE_PATTERN, LIBRARY_PACKAGE_NAME, verbose=verbose)


def main(sys_argv):
    """
    Execute this script's main function, and return the exit status.

    """
    # TODO: follow all of the recommendations here:
    # http://www.artima.com/weblogs/viewpost.jsp?thread=4829

    # Configure logging before entering the try block to ensure that
    # we can log errors in the corresponding except block.
    verbose = should_log_verbosely(sys_argv)
    configure_logging(logging.DEBUG if verbose else logging.INFO)

    try:
        try:
            process_args(sys_argv)
        except Error as err:
            _log.error(err)
            raise
    except UsageError as err:
        print "\nPass -h or --help for help documentation and available options."
        return 2
    except Error, err:
        return 1


class Error(Exception):
    """Base class for exceptions raised explicitly in this project."""
    pass


class UsageError(Error):
    """Exception class for command-line syntax errors."""
    pass


# We subclass optparse.OptionParser to customize the error behavior.
class TesterOptionParser(OptionParser):

    def error(self, message):
        """
        Handle an error occurring while parsing command arguments.

        This method overrides the OptionParser base class's error().  The
        OptionParser class requires that this method either exit or raise
        an exception.

        """
        raise UsageError(message)


class DocTestsTestCase(unittest.TestCase):

    """
    A unittest TestCase that runs the doc tests.

    We wrap the doc tests inside a TestCase so that the aggregate unittest
    test run will reflect the success or failure of the doc tests.
    In particular, the success or failure of the doc tests will be reflected
    in the exit status.

    """
    def __init__(self, verbose=False):
        super(DocTestsTestCase, self).__init__()
        self.__verbose = verbose

    def setUp(self):
        # TODO: Find a better way to move to the start of the next line.
        print
        _log.info("Running all doc tests as a single unit test...")

    # The name "runTest" is a magic value.
    def runTest(self):
        (failure_count, test_count) = run_doc_tests(verbose=self.__verbose)
        if failure_count is 0:
            return

        msg = "%s out of %s doc tests failed." % (failure_count, test_count)
        # We log the error before calling the assertion.  Otherwise, the
        # message will not be logged on assertion failure.
        _log.error(msg)
        self.assertEquals(failure_count, 0, msg)


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
    def __init__(self, verbose=False):
        super(TestLoader, self).__init__()
        self.__verbose = verbose


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
        doc_tests_suite = create_doc_tests_suite(self.suiteClass, verbose=self.__verbose)
        suites.append(doc_tests_suite)

        return self.suiteClass(suites)
