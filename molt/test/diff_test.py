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

from molt.diff import are_fuzzy_equal


class AreFuzzyEqualTestCase(unittest.TestCase):

    def _assert(self, assert_func, u1, u2):
        # TODO: toggle the inner symbol depending on whether testing true or false.
        msg = "%s ?= %s" % (repr(u1), repr(u2))
        assert_func(are_fuzzy_equal(u1, u2), msg=msg)

    def _assert_equal(self, u1, u2):
        self._assert(self.assertTrue, u1, u2)

    def _assert_not_equal(self, u1, u2):
        self._assert(self.assertFalse, u1, u2)

    def _assert_both_not_equal(self, u1, u2):
        self._assert_not_equal(u1, u2)
        self._assert_not_equal(u2, u1)

    def test_same__basic(self):
        self._assert_equal(u"abc", u"abc")

    def test_different__basic(self):
        self._assert_not_equal(u"abc", u"abcd")

    def test_different_numbers_of_lines(self):
        self._assert_both_not_equal(u"a\nb", u"ab")

    def test_marker__beginning_of_line(self):
        self._assert_equal(u"abc", u"...abc")

    def test_marker__beginning_of_line__wrong_string(self):
        self._assert_not_equal(u"...abc", u"abc")

    def test_marker__middle_of_line__equal(self):
        self._assert_equal(u"abcdef", u"abc...xyz")

    def test_marker__middle_of_line__not_equal(self):
        self._assert_not_equal(u"abcdef", u"def...xyz")

    def test_marker__first_line_too_short(self):
        """
        Test that a too-short first line does not raise an exception.

        """
        self._assert_not_equal(u"", u"a...b")
