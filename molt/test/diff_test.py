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
Unit tests for diff.py.

"""

import os
import unittest

from molt.diff import match_fuzzy, FileComparer
from molt.test.harness import config_load_tests


# The subdirectory of the test data directory containing the test data for
# MatchFilesTestCase.  The path is relative to the test data directory.
_MATCH_FILES_DIR = 'diff__FileComparer'


# Trigger the load_tests protocol.
load_tests = config_load_tests


class AreFuzzyEqualTestCase(unittest.TestCase):

    def _assert(self, u1, u2, expected):
        msg_symbol = '!=' if expected else '=='
        msg = "%s %s %s" % (repr(u1), msg_symbol, repr(u2))
        self.assertIs(expected, match_fuzzy(u1, u2), msg=msg)

    def _assert_match(self, u1, u2):
        """
        Assert that the two strings match.

        """
        self._assert(u1, u2, True)

    # TODO: rename _assert_not_match.
    def _assert_not_match(self, u1, u2):
        self._assert(u1, u2, False)

    def _assert_both_not_equal(self, u1, u2):
        self._assert_not_match(u1, u2)
        self._assert_not_match(u2, u1)

    def test_same__basic(self):
        self._assert_match(u"abc", u"abc")

    def test_different__basic(self):
        self._assert_not_match(u"abc", u"abcd")

    def test_different_numbers_of_lines(self):
        self._assert_both_not_equal(u"a\nb", u"ab")

    def test_marker__beginning_of_line(self):
        self._assert_match(u"abc", u"...abc")

    def test_marker__beginning_of_line__wrong_string(self):
        self._assert_not_match(u"...abc", u"abc")

    def test_marker__middle_of_line__equal(self):
        self._assert_match(u"abcdef", u"abc...xyz")

    def test_marker__middle_of_line__not_equal(self):
        self._assert_not_match(u"abcdef", u"def...xyz")

    def test_marker__first_line_too_short(self):
        """
        Test that a too-short first line does not raise an exception.

        """
        self._assert_not_match(u"", u"a...b")


class MatchFilesTestCase(unittest.TestCase):

    """
    Tests the match_files() function.

    """

    @property
    def _data_dir(self):
        data_dir = self.test_config.project.test_data_dir
        return os.path.join(data_dir, _MATCH_FILES_DIR)

    def _assert(self, file_name1, file_name2, expected, match_func=None):
        """
        Assert whether the contents of the two files match.

        """
        path1, path2 = (os.path.join(self._data_dir, name) for name in (file_name1, file_name2))

        fcmp = FileComparer(path1, path2, match=match_func)
        actual = fcmp.compare()

        # TODO: share code with AssertStringMixin's formatting code.
        msg = """\
File contents %smatch:

  left:  %s
  right: %s""" % ('' if actual else 'do not ', repr(fcmp.left), repr(fcmp.right))

        self.assertIs(expected, actual, msg=msg)

    def _assert_fuzzy(self,  file_name1, file_name2, expected):
        self._assert(file_name1, file_name2, expected, match_func=match_fuzzy)

    def test_match(self):
        self._assert('abc.txt', 'abc.txt', True)

    def test_not_match(self):
        self._assert('abc.txt', 'def.txt', False)
        self._assert('def.txt', 'abc.txt', False)

    def test_match_func(self):
        self._assert_fuzzy('abc.txt', 'has_marker.txt', True)
        self._assert_fuzzy('has_marker.txt', 'abc.txt', False)
