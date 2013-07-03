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

import molt.diff as diff
from molt.diff import match_fuzzy
from molt.test.harness import config_load_tests


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


class DifferTestCase(unittest.TestCase):

    def _differ(self, fuzz="..."):
        return diff._LineComparer(fuzz=fuzz)

    def _message(self, actual, expected, fuzz):
        return """Parameters:
actual:   %r
expected: %r
fuzz:     %r
""" % (actual, expected, fuzz)

    def _assert(self, assert_func, actual, expected, fuzz):
        result = self._diff_line(actual, expected, fuzz)
        assert_func(result, msg=self._message(actual, expected, fuzz))

    def _diff_line(self, actual, expected, fuzz=None):
        differ = self._differ(fuzz=fuzz)
        return differ.check_lines(actual, expected)

    def _assert_lines_equal(self, actual, expected, fuzz=None):
        self._assert(self.assertTrue, actual, expected, fuzz)

    def _assert_lines_unequal(self, actual, expected, fuzz=None):
        self._assert(self.assertFalse, actual, expected, fuzz)

    def test_re_pattern(self):
        differ = self._differ(fuzz="...")
        self.assertEqual(differ.re_pattern(r"ab"), r"^ab$")
        self.assertEqual(differ.re_pattern(r"a.b"), r"^a\.b$")
        self.assertEqual(differ.re_pattern(r"a...b"), r"^a.*b$")
        self.assertEqual(differ.re_pattern(r"a....b"), r"^a.*\.b$")
        self.assertEqual(differ.re_pattern(r"a...b...c"), r"^a.*b.*c$")

    @unittest.skip("TODO: fix this test")
    def test_diff_line(self):
        self._assert_lines_equal("abc", "abc")
        self._assert_lines_unequal(" abc ", "abc")
        self._assert_lines_unequal("axxxc", "abc")
        self._assert_lines_equal("axxxc", "a...c", "...")
        self._assert_lines_equal("axxxcyyd", "a...c...d", "...")

    def _diff_lines(self, actual, expected, fuzz=None):
        differ = self._differ(fuzz=fuzz)
        return differ.diff_lines(actual, expected)

    def _assert_diff_lines(self, actual, expected, actual_index,
                           expected_index=None, fuzz=None):
        if expected_index is None:
            expected_index = actual_index
        info = self._diff_lines(actual, expected, fuzz)
        self.assertEqual((info.actual_index, info.expected_index),
                         (actual_index, expected_index))

    @unittest.skip("TODO: fix this test")
    def test_diff_index_equal_strings(self):
        with self.assertRaises(Exception) as cm:
            self._diff_lines("abc", "abc")
        ex = cm.exception
        self.assertEqual(str(ex), "strings not different")

    @unittest.skip("TODO: fix this test")
    def test_diff_lines(self):
        self._assert_diff_lines("a", "", 0)
        self._assert_diff_lines("", "a", 0)
        self._assert_diff_lines("a", "b", 0)
        self._assert_diff_lines("a", "ab", 1)
        self._assert_diff_lines("", "a...", 0, 0, fuzz="...")
        self._assert_diff_lines("ablahcefgdefg", "a...c...d", 10, 9, fuzz="...")
