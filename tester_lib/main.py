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
Runs all unit tests and doctests in the project.

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
interactive code snippets that appear in project documenation.  This
script looks for doctests in essentially all project files, for example
in the project's README file and in all of the Python code's docstrings.
A doctest might look like this:

>>> 1 + 1
2

For unified reporting reasons, this script runs all tests as unit tests,
including the doctests.  Each file of doctests corresponds to a single
unittest test case."""


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

    _log.debug("Verbose logging enabled.")


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


def create_doctest_suites(module_names, paths):
    """
    Return a list of TestSuite instances that contain the doctests.

    """
    suites = []

    for module in module_names:
        suite = doctest.DocTestSuite(module)
        suites.append(suite)

    for path in paths:
        suite = doctest.DocFileSuite(README_PATH)
        suites.append(suite)

    return suites


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

    argv = ['']

    # unittest.TestLoader's constructor, which is called directly by
    # unittest.main(), does not permit the defaultTest parameter to be
    # a list of test names -- only one name.  So we pass the test names
    # instead using the argv parameter.
    argv.extend(module_names)

    # Python's unittest module didn't add a verbosity parameter to
    # unittest.main() until Python 2.7.  However, we can bypass this
    # limitation by passing the verbosity to a test runner instance directly.
    # That is how unittest.main() uses the parameter internally.  If we
    # didn't have this option, we could instead have included "--verbose",
    # etc. in the argv parameter that we pass.
    #
    # The verbosity parameter: 0 for quiet, 1 for the default, 2 for verbose.
    # TODO: also add support for --quiet.
    verbosity = 2 if verbose else 1

    # We construct a custom test runner to avoid unittest.main()'s
    # Python 2.6 behavior of always exiting.  See UnittestTestRunner's
    # docstring for more details.
    test_runner = UnittestTestRunner(verbosity=verbosity)

    _log.info("Running molt tests...")

    try:
        unittest.main(testLoader=UnittestTestLoader(), testRunner=test_runner,
                      module=None, argv=argv)
    except UnittestTestRunnerResult as err:
        result = err.result

    return result.wasSuccessful()


def process_args(sys_argv):
    """Run all unit tests."""

    (options, args) = parse_args(sys_argv)

    verbose = options.verbose

    module_dir = os.path.dirname(__file__)

    top_dir = os.path.join(module_dir, os.pardir, LIBRARY_PACKAGE_NAME)
    was_successful = run_unit_tests(top_dir, TEST_MODULE_PATTERN, LIBRARY_PACKAGE_NAME, verbose=verbose)

    return 0 if was_successful else 1


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
            status = process_args(sys_argv)
        except Error as err:
            _log.error(err)
            raise
    except UsageError as err:
        print "\nPass -h or --help for help documentation and available options."
        status = 2
    except Error, err:
        status = 1

    return status


class Error(Exception):
    """Base class for exceptions raised explicitly in this project."""
    pass


class UsageError(Error):
    """Exception class for command-line syntax errors."""
    pass


class UnittestTestRunnerResult(Error):
    """Raised by UnittestTestRunner to communicate a test run result."""
    def __init__(self, result):
        self.result = result


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


class UnittestTestRunner(unittest.TextTestRunner):

    """
    A unittest test runner for use by this package.

    This test runner differs from unittest's default TextTestRunner because
    its run() method raises an exception after running tests instead of
    returning the result.  This is a hack to get around the fact that
    unittest.main() calls sys.exit() immediately after running the tests.
    Only in Python 2.7 does the unittest module provide a way to bypassing
    the system exit.

    By having the TestRunner raise an exception, we can leave unittest.main()
    before it calls sys.exit().  We include the result in the raised
    exception so that the caller can handle the error and read the result.

    """

    def run(self, test):
        """
        Run the given test case or test suite, and raise an exception.

        This method raises a UnittestTestRunnerResult exception that
        contains the result of the test run.

        """
        result = super(UnittestTestRunner, self).run(test)

        raise UnittestTestRunnerResult(result)


class UnittestTestLoader(unittest.TestLoader):

    """
    In addition to loading the doctests as unit tests, this TestLoader
    differs from unittest's default TestLoader by providing additional
    diagnostic information when an AttributeError occurs while loading a
    module.

    Because of Python issue 7559:

      http://bugs.python.org/issue7559#

    the unittest module masks ImportErrors andthe name of the offending
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

        # TODO: the global variable should be passed as a parameter, e.g.
        # via the class's constructor.
        paths = [README_PATH]
        doctest_suites = create_doctest_suites(module_names=names, paths=paths)

        suites.extend(doctest_suites)

        return self.suiteClass(suites)
