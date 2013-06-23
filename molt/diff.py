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
Molt-specific support for diffing files and directories.

Molt requires its own diff functions partly because of its fuzzy-match
requirements.  For example, Python's standard library difflib module
does not support fuzzy matching in the way that Molt requires.

"""

from __future__ import absolute_import

import logging
import os
import re
import sys

from molt.defaults import FUZZY_MARKER
from molt.general.dirdiff import compare_files, DirDiffer


_log = logging.getLogger(__name__)


# TODO: switch from using this to the Differ class below.
def match_fuzzy(u1, u2, marker=None):
    """
    Return whether the given unicode strings are "fuzzily" equal.

    Fuzzily equal means equal except possibly for characters at or
    beyond a fuzzy marker on a line of the string.  For example--

    >>> match_fuzzy('abcdef', 'abcdef')
    True
    >>> match_fuzzy('abcdef', 'abcwxyz')
    False
    >>> match_fuzzy('abcdef', 'abc...wxyz', marker='...')
    True
    >>> match_fuzzy('abc...def', 'abcwxyz', marker='...')
    False

    Observe that the fuzzy marker is only respected when occurring
    in the second string.  For this reason, the second string can often
    be interpreted as the "expected" string in the pair (i.e. because in
    most scenarios it is the expected string that provides leeway
    for an actual value).

    """
    if marker is None:
        marker = FUZZY_MARKER

    lines1, lines2 = (u.splitlines(True) for u in (u1, u2))

    if len(lines1) != len(lines2):
        return False

    for line1, line2 in zip(lines1, lines2):
        if line1 == line2:
            continue
        # Otherwise, check for ellipses in the second line.
        i = line2.find(marker)
        # Note that an expression like `'abc'[:5]`, for example, will not
        # raise an exception.
        if i < 0 or line1[:i] != line2[:i]:
            return False

    return True

# TODO: Finish this class.  It should internally call dirdiff.Differ.diff().
#   The function can return the line number and character number at
#   the first difference.
class DirComparer(object):

    def __init__(self, fuzzy=False):
        self.fuzzy = fuzzy

    def compare(self, path1, path2):
        pass


class DiffInfo(object):

    def __init__(self, actual_index, expected_index):
        self.actual_index = actual_index
        self.expected_index = expected_index


# TODO: finish this class
class DiffPrinter(object):
    # abcde
    #   ^ index=2
    # abcef
    #   ^ index=2
    pass


# TODO: finish this class
class Differ(object):

    def __init__(self, fuzz=None):
        self.fuzz = fuzz

    def use_fuzz(self, expected):
        return self.fuzz is not None and self.fuzz in expected

    def _expected_parts(self, expected):
        return expected.split(self.fuzz)

    def _re_pattern(self, parts):
        return "^%s" % ".*".join([re.escape(part) for part in parts])

    def re_pattern(self, expected):
        """
        Converted an expected string into a regular expression pattern.

        For example,
        """
        parts = self._expected_parts(expected)
        return "%s$" % self._re_pattern(parts)

    def check_lines(self, actual, expected):
        """
        Return whether the given lines are equal.

        Neither string should contain a newline.

        """
        if not self.use_fuzz(expected):
            return actual == expected
        # Otherwise, use fuzzy matching.
        return re.match(self.re_pattern(expected), actual) is not None

    def _diff_index_without_fuzz(self, actual, expected):
        for i in range(max(len(actual), len(expected))):
            try:
                if actual[i] == expected[i]:
                    continue
            except IndexError:
                # Then one string is longer than the other.
                pass
            # Then there is a difference at index i.
            return DiffInfo(i, i)
        raise Exception("strings not different")

    def _diff_index_with_fuzz(self, actual, expected):
        parts = self._expected_parts(expected)
        while True:
            match = re.match(self._re_pattern(parts), actual)
            if match is not None:
                # Then the initial segment matches.
                break
            if not parts[-1]:
                parts.pop()
            # Remove the last character from the last string.
            parts[-1] = parts[-1][:-1]
        actual_index = len(match.group(0))
        expected_index = len(self.fuzz.join(parts))
        return DiffInfo(actual_index, expected_index)

    def diff_lines(self, actual, expected):
        """
        Return the index at which the two strings diverge.

        """
        if self.use_fuzz(expected):
            return self._diff_index_with_fuzz(actual, expected)
        return self._diff_index_without_fuzz(actual, expected)
