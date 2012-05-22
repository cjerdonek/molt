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
Unit tests for the main module.

"""

import logging
import unittest
from unittest import TestCase

from molt.main import Error, run_molt


def test_gen(tests):
    """
    Return a generator over all TestCase instances recursively in tests.

    For example--

    for test in test_gen(tests):
        print test

    Arguments:

      tests: a TestCase instance, TestSuite instance, or iterable of
        TestCase and TestSuite instances.

    """
    if isinstance(tests, TestCase):
        yield tests
        return
    # Otherwise, we have an iterable or a TestSuite instance.
    for test in tests:
        for test2 in test_gen(test):
            yield test2


def load_tests(loader, tests, pattern):
    for test in test_gen(tests):
        test.util = loader.util

    return unittest.TestSuite(tests)


class MockLogging(object):

    """Mock logging for testing purposes."""

    def configure_logging(self, sys_argv):
        self.argv = sys_argv


class CreateDemoTestCase(unittest.TestCase):

    """Test --create-demo mode."""

    def test_load_tests(self):
        with self.util.sandbox_dir(self, "abc") as dir_path:
            self.assertEquals("foo", "foo")

    def test_output_directory(self):
        pass


class MainTestCase(unittest.TestCase):

    """Test the main() function."""

    # TODO: test cases for UsageError and Exception.
    # TODO: prevent the 'No handlers could be found for logger "molt"'
    # message from showing up.

    def setUp(self):
        self.logging = MockLogging()

    def test_error(self):
        def process_args(sys_argv):
            raise Error("test")

        sys_argv = []
        result = run_molt(sys_argv, configure_logging=self.logging.configure_logging,
                          process_args=process_args)
        self.assertEquals(result, 1)
        self.assertTrue(self.logging.argv is sys_argv)

