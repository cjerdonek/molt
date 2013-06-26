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

import itertools
import logging
import os
import re
import sys

from molt.defaults import FUZZY_MARKER
from molt.general.dirdiff import compare_files, DirDiffer


_log = logging.getLogger(__name__)


# TODO: switch from using this to the _LineDiffer class below.
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


class MoltComparer(object):

    def __init__(self, fuzz):
        self.fuzz = fuzz

    def check_string(self, s1, s2):
        """
        Return whether a given unicode string matches an expected one.

        """
        lines1, lines2 = (u.splitlines(True) for u in (actual, expected))

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


class _DiffInfo(object):
    pass


# The implementation of this class depends only on _DiffInfo.
class DiffDescriber(object):

    def __init__(self, context=2):
        """

        context: the number of lines of context to include.

        """
        self.context = context

    def _format_line_raw(self, line_index, contents):
        return "%d:%s" % (line_index + 1, contents)

    def _format_line(self, line, line_index):
        contents = " %r" % line
        return self._format_line_raw(line_index, contents)

    def _format_line_with_char(self, line, line_index, char_index):
        contents = "%d %r" % (char_index + 1, (line[:char_index], line[char_index:]))
        return self._format_line_raw(line_index, contents)

    def _format_seq(self, lines, report, min_index, max_index, char_index):
        ilines = itertools.islice(lines, min_index, max_index)
        for i, line in enumerate(ilines, start=min_index):
            line = self._format_line(line, i)
            report.append(" %s" % line)
        # Then add the line with the difference.
        i += 1
        try:
            line = lines[i]
        except IndexError:
            line = None
        if char_index is None:
            line = self._format_line(line, i)
        else:
            line = self._format_line_with_char(line, i, char_index)
        report.append("*%s" % line)

    def describe(self, info, seqs):
        """
        Describe the difference between the two sequences of lines.

        Returns a sequence of strings.

        """
        max_index = info.line_index
        min_index = max(0, max_index - self.context)
        chars = info.char_indices
        char_desc = ("" if chars[0] is None else
                     ", characters %d and %d, resp" %
                     tuple(i + 1 for i in chars))
        header = ("first difference found at line %d%s;\n"
                  "showing actual then expected:" % (max_index + 1, char_desc))
        report = [header]
        for char_index, lines in zip(info.char_indices, seqs):
            self._format_seq(lines, report, min_index, max_index, char_index)
            report.append(3 * "-")
        report.pop()
        return report


# TODO: finish this class
class _LineDiffer(object):

    def __init__(self, fuzz=None):
        self.fuzz = fuzz

    def has_fuzz(self, expected):
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
        # TODO: switch from $ to \Z and add a test case for this difference.
        return "%s$" % self._re_pattern(parts)

    def _lines_equal(self, line1, line2):
        """
        Return whether the given lines are equal.

        Neither string should contain a newline.

        """
        if not self.has_fuzz(line2):
            return line1 == line2
        # Otherwise, use fuzzy matching.
        return re.match(self.re_pattern(line2), line1) is not None

    def _compare_lines_exact(self, line1, line2):
        """
        Return the string indices at which the two lines differ.

        Arguments:
          line1: a unicode string.
          line2: a unicode string that compares differently from line1.

        """
        for i, chars in enumerate(zip(line1, line2)):
            print i, chars
            if chars[0] == chars[1]:
                continue
            # Otherwise, the characters differ.
            return [i, i]
        # Otherwise, one line is longer than the other.
        indices = [i + 1, None]
        if len(line1) < len(line2):
            indices.reverse()
        return indices

    def _compare_lines_fuzzy(self, line1, line2):
        """
        Return the string indices at which the two lines differ.

        Arguments:
          line1: a unicode string.
          line2: a unicode string that compares differently from line1.

        """
        line2_parts = self._expected_parts(line2)
        while True:
            m = re.match(self._re_pattern(line2_parts), line1)
            if m is not None:
                # Then the initial segment matches.
                break
            if not line2_parts[-1]:
                line2_parts.pop()
            # Remove the last character from the last string.
            line2_parts[-1] = line2_parts[-1][:-1]
        indices = [len(s) for s in (m.group(0), self.fuzz.join(line2_parts))]
        for i, (char_index, line) in enumerate(zip(indices, (line1, line2))):
            try:
                line[char_index]
            except IndexError:
                indices[i] = None
        return indices

    def _compare_lines(self, line1, line2):
        """
        Return the string indices at which the two lines differ.

        Arguments:
          line1: a unicode string.
          line2: a unicode string that compares differently from line1.

        """
        if self.has_fuzz(line2):
            return self._compare_lines_fuzzy(line1, line2)
        return self._compare_lines_exact(line1, line2)

    def compare_sequences(self, seq1, seq2):
        """
        Compare two sequences of unicode lines.

        Returns a DiffInfo instance if the sequences differ.  Otherwise,
        returns None.

        """
        for i, lines in enumerate(zip(seq1, seq2)):
            if self._lines_equal(*lines):
                continue
            # Otherwise, the lines are different.
            info = DiffInfo()
            info.char_indices = self._compare_lines(*lines)
            line_indices = [i, i]
            break
        else:
            # Check whether there are additional lines.
            c = cmp(len(seq1), len(seq2))
            if c == 0:
                return None
            info = DiffInfo()
            line_indices = [i + 1, None]
            if c < 0:
                # Then seq2 has more lines.
                line_indices.reverse()
        info.line_indices = line_indices
        return info


if __name__ == "__main__":
    seq1 = ["a", "b", "c", "d", "e"]
    seq2 = ["a", "d", "e", "g"]
    formatter = DiffDescriber()
    info = _DiffInfo()
    info.line_index = 3
    info.char_indices = (0, 1)
    report = formatter.describe(info, [seq1, seq2])
    print "\n".join(report)
    exit()


    printer = DiffPrinter()
    differ = _LineDiffer(fuzz=".")
    # abckxy
    # abc.xyz
    #
    line1 = "abkvvx"
    line2 = "ab.xkkk"
    print line1
    print line2
    char_indices = differ._compare_lines(line1, line2)
    info = differ.compare_sequences(["a"], ["b"])
    #info = differ.compare_sequences(["a", line1], ["b", line2])
    print info.__dict__

    print char_indices
    exit()
    formatted = printer.format_line(info, actual, expected)
    print("\n".join(formatted))
