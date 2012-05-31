# encoding: utf-8
#
# Copyright (C) 2012 Chris Jerdonek. All rights reserved.
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
Provides a load_tests wrapper for configuring tests.

Usage:

In a module containing unit tests that require configuration, include
the following (or an equivalent):

    from molt.test.harness.loading import config_load_tests

    # Trigger the load_tests protocol.
    load_tests = config_load_tests

"""

from __future__ import absolute_import

from unittest import TestCase, TestSuite


def _test_gen(tests):
    """
    Return a generator over all TestCase instances recursively in tests.

    Sample usage--

    for test in test_gen(tests):
        print test

    The point is that TestSuite.__iter__() only provides direct access to
    child tests and not to grandchild tests, etc. which this function
    provides.  Also see--

      http://docs.python.org/library/unittest.html#unittest.TestSuite.__iter__

    Arguments:

      tests: a TestCase instance, TestSuite instance, or iterable of
        TestCase and TestSuite instances.

    """
    if isinstance(tests, TestCase):
        yield tests
        return
    # Otherwise, we have an iterable or a TestSuite instance.
    for test in tests:
        for test2 in _test_gen(test):
            yield test2


def config_load_tests(loader, tests, pattern):
    """
    A load_tests protocol implementation that sets the test_config attribute.

    Returns a unittest.TestSuite instance.

    """
    for test in _test_gen(tests):
        test.test_config = loader.test_config

    return TestSuite(tests)


class TestConfig(object):

    """
    A container for test configuration data for Molt test runs.

    """

    def __init__(self, test_run_dir):
        """
        Arguments:

          test_run_dir: the "sandbox" directory in which to write temporary
            test data (e.g. the directory outputs of rendering test project
            templates).

        """
        self.test_run_dir = test_run_dir
