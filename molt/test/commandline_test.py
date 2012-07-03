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
Unit tests for commandline.py.

"""

import unittest

from molt.commandline import parse_args


class ParseArgsTestCase(unittest.TestCase):

    def test_no_prog(self):
        """
        Check that argv[0] is not interpreted as an option.

        """
        def _assert(argv, expected):
            pargs = parse_args(argv)
            self.assertIs(pargs.run_test_mode, expected)

        _assert(['prog', '--run-tests'], True)
        _assert(['--run-tests'], False)

    # TODO: confirm the error behavior we want.
    def test_two_directories(self):
        """
        Check that providing two directories causes an error.

        """
        argv = ['prog', 'foo', 'bar']
        pargs = parse_args(argv)
        self.assertIs(pargs.input_directory, None)

    def test_test_names__not_running_tests(self):
        argv = ['prog', 'foo']
        pargs = parse_args(argv)
        self.assertIs(pargs.test_names, None)

    def test_test_names__running_tests__no_names(self):
        argv = ['prog', '--run-tests']
        pargs = parse_args(argv)
        self.assertListEqual(pargs.test_names, [])

    def test_test_names__running_tests__one_name(self):
        argv = ['prog', '--run-tests', 'foo']
        pargs = parse_args(argv)
        self.assertListEqual(pargs.test_names, ['foo'])

    def test_run_test_mode__false(self):
        argv = ['prog']
        pargs = parse_args(argv)
        self.assertIs(pargs.run_test_mode, False)

    def test_run_test_mode__false_with_name(self):
        argv = ['prog', 'foo']
        pargs = parse_args(argv)
        self.assertIs(pargs.run_test_mode, False)

    def test_run_test_mode__true(self):
        argv = ['prog', '--run-tests']
        pargs = parse_args(argv)
        self.assertIs(pargs.run_test_mode, True)

    def test_run_test_mode__true_with_test_name(self):
        argv = ['prog', '--run-tests', 'foo']
        pargs = parse_args(argv)
        self.assertIs(pargs.run_test_mode, True)

    def test_input_directory__provided(self):
        argv = ['prog', 'foo']
        pargs = parse_args(argv)
        self.assertEquals(pargs.input_directory, 'foo')

    def test_input_directory__not_provided(self):
        argv = ['prog']
        pargs = parse_args(argv)
        self.assertIs(pargs.input_directory, None)

    def test_input_directory__running_tests(self):
        """
        Check that test names are not interpreted as a template directory.

        """
        argv = ['prog', '--run-tests', 'foo', 'bar']
        pargs = parse_args(argv)
        self.assertIs(pargs.input_directory, None)

