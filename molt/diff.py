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

import molt.defaults as defaults
import molt.general.dirdiff as dirdiff
# TODO: remove these from ... imports.
from molt.general.dirdiff import compare_files, DirComparer
import molt.general.io as molt_io


_ENCODING = defaults.FILE_ENCODING

_log = logging.getLogger(__name__)


class _DiffInfo(object):

    def __init__(self, line_index=None, char_indices=None):
        """
        TODO: document the attributes.  In particular, is line_index a
        valid line for both sequences?

        """
        if char_indices is None:
            char_indices = (None, None)
        self.line_index = line_index
        self.char_indices = char_indices


# The implementation of this class depends only on _DiffInfo's interface.
class _DiffDescriber(object):

    """
    Responsible for the string describing the difference between two strings.

    """

    # TODO: remove this.
    leading_chars = "+-"

    def __init__(self, indent, context=2):
        """

        context: the number of lines of context to include.

        """
        self.context = context
        self.indent = indent

    def _make_header_line(self, info):
        """
        Return the header line ending in a newline.

        """
        chars = info.char_indices
        char_desc = ("" if chars[0] is None else
                     ", chars %d and %d" %
                     tuple(i + 1 for i in chars))
        return ("first difference at line %d%s\n" %
                (info.line_index + 1, char_desc))

    def _make_view_header_line(self, label):
        return "%s view:\n" % label

    # TODO: address justification in transition from 9 to 10, for example.
    def _format_line2(self, contents, line_number, sep=None):
        if sep is None:
            sep = " "
        # Add one to the index for 1-based line numbers.
        return "%d:%s%s" % (line_number, sep, contents)

    # TODO: define a method that takes a generates the display view for one
    # of the two strings.
    def _format_with_line_numbers(self, seq, start_index):
        lines = []
        for i, line in enumerate(seq, start=start_index):
            line = "%s%d:%s" % (i, line)
            lines.append(line)
        return lines

    def _seq_to_display_view(self, seq, min_index, max_index, indent):
        """
        Return the rendered view of a sequence.

        Returns a sequence of lines.  Each ends in a newline.

        """
        lines = []
        # The sequence may or may not contain the final index (slicing does
        # not error out even if it does not).
        for i, line in enumerate(seq[min_index:max_index + 1], start=min_index):
            line = "%s%d:%s" % (indent, i, line)
            lines.append(line)
        # Make sure final line ends in a newline.
        if lines and lines[-1] and lines[-1][-1] != "\n":
            lines[-1] += "\n"
        return lines

    def _format_line_raw(self, line_index, contents):
        return "%d:%s" % (line_index + 1, contents)

    def _format_line(self, line, line_index):
        """
        Example:

        >>> d = _DiffDescriber()
        >>> d._format_line("abcdef", 9)
        "10: 'abcdef'"

        """
        contents = " %r" % line
        return self._format_line_raw(line_index, contents)

    def _format_line_with_char(self, line, line_index, char_index):
        """
        Example:

        >>> d = _DiffDescriber()
        >>> d._format_line_with_char("abcdef", 9, 3)
        "10:4 ('abc', 'def')"

        """
        contents = "%d %r" % (char_index + 1, (line[:char_index], line[char_index:]))
        return self._format_line_raw(line_index, contents)

    def _format_seq(self, seq, report, min_index, max_index, char_index, lead_char):
        view = self._seq_to_display_view(seq, min_index, max_index, lead_char)
        report.extend(view)
        for i, line in enumerate(seq[min_index:max_index], start=min_index):
            line = self._format_line(line, i)
            report.append(" %s\n" % line)
        # Then add the line with the difference.
        try:
            line = seq[max_index]
        except IndexError:
            line = None
        if char_index is None:
            line = self._format_line(line, max_index)
        else:
            line = self._format_line_with_char(line, max_index, char_index)
        report.append("*%s" % line)

    # TODO: add tests for the edge cases mentioned in the code comments.
    def _make_seq_display_view(self, seq, index1, index2):
        seq = seq[index1:index2 + 1]
        # Handle the last line of seq not ending in a newline.
        if seq and (not seq[-1] or seq[-1][-1] != "\n"):
            seq[-1] += "\n"
        sep = ' '
        lines = []
        # Make sure the index is defined in case of any empty loop.
        i = None
        # TODO: cover case of not looping at all.
        max_index = index2 - index1
        for i, line in enumerate(seq[:max_index], start=index1):
            # Add one for 1-based line numbers.
            line = self._format_line2(line, i + 1)
            lines.append("  " + line)
        # Special case the final index (the line with the difference) to
        # prefix it with a symbol and handle the case of the last line not
        # existing.
        try:
            line = seq[max_index]
        except IndexError:
            line = "<no line>"
            sep = ''
        # Add one for 1-based line numbers.
        line = self._format_line2(line, index2 + 1, sep=sep)
        lines.append(" *" + line)
        return lines

    def _make_display_view(self, seqs, index1, index2):
        header = self._make_view_header_line('display')
        lines = [header]
        for seq in seqs:
            new_lines = self._make_seq_display_view(seq, index1, index2)
            lines.extend(new_lines)
            lines.append("----\n")
        # Only add the separator between the two.
        lines.pop()
        return lines

    def describe(self, info, seqs):
        """
        Describe the difference between two sequences of lines.

        Returns a sequence of strings describing the difference.  Each
        string ends in a newline except for the last.

        """
        # The line at which the first difference occurs.
        line_index2 = info.line_index
        line_index1 = max(0, line_index2 - self.context)
        char_indices = info.char_indices

        header = self._make_header_line(info)
        report = [header]
        display_view = self._make_display_view(seqs, line_index1, line_index2)
        report.extend(display_view)

        # TODO: want a method that takes a sequence of lines ending in
        # newlines or not, and then formats it with line numbers.
        # This way it can be used against the sequence of as-is lines
        # as in the display view.  In this way, the detail view will
        # require building the lines ending in newlines (except for the
        # last one) using repr().
        indent = "  "
        report.append(self._make_view_header_line('detail'))
        labels = ('actual', 'expected')
        for label, char_index, seq in zip(labels, char_indices, seqs):
            report.append("--- %s:\n" % label)
            self._format_seq(seq, report, line_index1, line_index2, char_index, "+")
        return report


# TODO: switch from using this to the _LineDiffer class below.
def match_fuzzy(u1, u2, marker=None):
    if marker is None:
        marker = defaults.DIFF_FUZZ

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


# TODO: remove this class.
class DirComparer(object):

    def __init__(self, fuzzy=False):
        self.fuzzy = fuzzy

    def compare(self, path1, path2):
        pass


# TODO: finish this class
class _LineComparer(object):

    """
    In the comparison methods of this class that accept a pair of strings,
    the second string should be the expected string.  Only in the second
    string can substrings be interpreted as fuzz.

    """

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

    def _lines_equal(self, lines):
        """
        Return whether the given lines are equal.

        Neither line should contain a newline before the last character.

        """
        line1, line2 = lines
        if not self.has_fuzz(line2):
            return line1 == line2
        # Otherwise, use fuzzy matching.
        return re.match(self.re_pattern(line2), line1) is not None

    def _compare_lines_exact(self, lines):
        """
        Return the pair of indices at which the two lines differ.

        Parameters:

          lines: a pair of unicode strings that compare differently.

        Example:

        >>> c = _LineComparer()
        >>> c._compare_lines_exact(("abc", "abx"))
        (2, 2)
        >>> c._compare_lines_exact(("abc", "a"))
        (1, 1)

        """
        for i, chars in enumerate(zip(*lines)):
            if chars[0] == chars[1]:
                continue
            # Otherwise, the characters differ.
            break
        else:
            # Otherwise, one line is longer than the other.
            i += 1
        return (i, i)

    def _compare_lines_fuzzy(self, lines):
        """
        Return the pair of indices at which the two lines differ.

        Parameters:

          lines: a pair of unicode strings that compare differently.

        Examples:

        >>> c = _LineComparer(fuzz="...")
        >>> c._compare_lines_fuzzy(("abc", "abx"))
        (2, 2)
        >>> c._compare_lines_fuzzy(("abc", "a"))
        (1, 1)
        >>> c._compare_lines_fuzzy(("a", "abc"))
        (1, 1)
        >>> c._compare_lines_fuzzy(("abc", "a...b"))
        (2, 5)
        >>> c._compare_lines_fuzzy(("abc", "a...x"))
        (3, 4)

        """
        line1, line2 = lines
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
        return tuple(len(s) for s in (m.group(0), self.fuzz.join(line2_parts)))

    def _compare_lines(self, lines):
        """
        Return the string indices at which the two lines differ.

        Parameters:
          line1: a unicode string.
          line2: a unicode string that compares differently from line1.

        """
        if self.has_fuzz(lines[1]):
            return self._compare_lines_fuzzy(lines)
        return self._compare_lines_exact(lines)

    def compare_seqs(self, seqs):
        """
        Compare two sequences of unicode lines.

        Returns a DiffInfo instance if the sequences differ.  Otherwise,
        returns None.

        """
        for line_index, lines in enumerate(zip(*seqs)):
            if self._lines_equal(lines):
                continue
            # Otherwise, the lines are different.
            char_indices = self._compare_lines(lines)
            break
        else:
            # Then all of the initial lines were equal.
            if len(seqs[0]) == len(seqs[1]):
                return None
            # Otherwise, one sequence has more lines, in which case
            # character indices do not apply.
            line_index += 1
            char_indices = None
        return _DiffInfo(line_index=line_index, char_indices=char_indices)


class _StringComparer(object):

    def __init__(self, indent, fuzz=None, context=None):
        if context is None:
            context = defaults.DIFF_CONTEXT
        if fuzz is None:
            fuzz = defaults.DIFF_FUZZ
        self.context = context
        self.fuzz = fuzz
        self.indent = indent

    def _describe(self, info, seqs):
        describer = _DiffDescriber(context=self.context, indent=self.indent)
        info = describer.describe(info, seqs)
        return info

    def compare_strings(self, strs):
        """
        Compare whether two unicode strings match.

        Returns an empty list if the strings match, otherwise a list of
        strings describing the difference.  Each string in the list ends
        in a newline.

        Parameters:

          strs: a pair of unicode strings.

        """
        seqs = tuple(u.splitlines(True) for u in strs)
        comparer = _LineComparer(fuzz=self.fuzz)
        info = comparer.compare_seqs(seqs)
        if info is None:
            return []
        return self._describe(info, seqs)


class _FileComparer(object):

    def __init__(self, scomparer):
        """
        Parameters:

          scomparer: an object with a compare_strings(strs) method.

        """
        self.scomparer = scomparer

    # TODO: handle binary files differently.
    # TODO: handle alternate encodings.
    def compare_files(self, paths):
        """
        Compare two text files.

        Returns an empty list if the strings match, otherwise a list of
        strings describing the difference.  Each string in the list ends
        in a newline.

        """
        strs = (molt_io.read(path, encoding=_ENCODING, errors=_ENCODING) for
                path in paths)
        return self.scomparer.compare_strings(strs)


class Customizer(object):

    """Customizes DirComparer behavior."""

    def __init__(self, fcomparer):
        """
        Parameters:

          comparer: an object with a compare_files(paths) method.

        """
        self.diff_files = {}
        self.fcomparer = fcomparer

    def files_same(self, path1, path2):
        _log.debug("comparing: %s and %s" % (path1, path2))
        info = self.fcomparer.compare_files((path1, path2))
        if not info:
            # Then the files are the same.
            return True
        return info

    def on_diff_file(self, rel_path, result):
        """
        Params:

          rel_path: the path of the differing files relative to the
            top-level directories of the directories being compared.

          result: the return value of compare_files.

        """
        _log.info("found different file: %s" % (rel_path, ))
        # Otherwise we have a list of strings describing the difference.
        self.diff_files[rel_path] = result


class Comparer(object):

    # TODO: update this docstring.
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

    In the comparison methods of this class that accept a pair of strings,
    the second string should be the expected string.  Only in the second
    string can substrings be interpreted as fuzz.

    """

    indent = "  "

    def __init__(self, writer=None, fuzz=None, context=None):
        """
        Parameters:

          writer: an object with a write() method.

        """
        if context is None:
            context = defaults.DIFF_CONTEXT
        if fuzz is None:
            fuzz = defaults.DIFF_FUZZ
        if writer is None:
            writer = sys.stderr
        self.context = context
        self.fuzz = fuzz
        self.writer = writer

    def _write(self, msg):
        self.writer.write(msg)

    def _customizer(self):
        scomparer = _StringComparer(fuzz=self.fuzz, context=self.context,
                                    indent=self.indent)
        fcomparer = _FileComparer(scomparer=scomparer)
        return Customizer(fcomparer=fcomparer)

    def _dir_comparer(self, customizer):
        return dirdiff.DirComparer(custom=customizer)

    def _lines_to_string(self, lines, indent=''):
        glue = "\n%s" % indent
        return glue.join(lines)

    def _make_attr_summary(self, info, header, attr_name, indent):
        """Return a multi-line string that does not end in a newline."""
        rel_paths = getattr(info, attr_name)
        lines = ["%s:%s" % (header, " none" if not rel_paths else "")]
        lines.extend(rel_paths)
        return self._lines_to_string(lines, indent=indent)

    def _make_file_summary(self, rel_path, desc):
        """Return a multi-line string that does not end in a newline."""
        header = "%s%s:\n" % (self.indent, rel_path)
        indent = 2 * self.indent
        lines = [header] + desc
        return indent.join(lines)

    def _make_summary(self, info, customizer):
        """
        Return a string suitable for displaying to the console.

        The string does not end in a newline.

        """
        if info.does_match():
            return "directories match."
        s = """\
directories don't match. showing differences between actual and expected:
+++ %r
--- %r""" % info.dirs
        sections = [s]
        headers = ["paths only in actual",
                   "paths only in expected",
                   "paths non-comparable in both",
                   "files differing in both"]
        for attr, header in zip(info.attr_names, headers):
            section = self._make_attr_summary(info, header, attr, indent='  ')
            sections.append(section)
        if info.diff_files:
            sections.append("file differences:")
        diff_results = customizer.diff_files
        for rel_path in info.diff_files:
            desc = diff_results[rel_path]
            section = self._make_file_summary(rel_path, desc)
            sections.append(section)
        return "\n".join(sections)

    def compare_strings(self, strs):
        """
        Compare whether two unicode strings match.

        Returns a list of strings describing the difference between
        the two strings, or an empty string if they match.

        Parameters:

          strs: a pair of unicode strings.

        """
        comparer = self._string_comparer()
        return comparer.compare_strings(strs)

    def compare_files(self, paths):
        """
        Compare whether two files match.

        Returns a list of strings describing the difference between
        the two files, or an empty string if they match.

        """
        comparer = self._file_comparer()
        return comparer.compare(paths)

    # TODO: this method should display detailed compare info.
    def compare_dirs(self, dirs):
        """
        Compare two directories.

        Writes
        Return whether two directories match.

        """
        customizer = self._customizer()
        dir_comparer = self._dir_comparer(customizer)
        info = dir_comparer.diff(*dirs)
        self._write(self._make_summary(info, customizer))
        return info.does_match()
