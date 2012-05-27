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
Provides test-related code that can be used by all tests.

"""

from __future__ import absolute_import

import logging
from textwrap import dedent

from molt.common import io
import molt.test


FUZZY_MARKER = "..."

test_logger = logging.getLogger(molt.test.__name__)


# The textwrap module does not expose an indent() method.
# Also see this issue: http://bugs.python.org/issue13857
def indent(text, prefix):
    lines = text.splitlines(True)
    def indent(line):
        if not line.strip():
            # Do not indent lines having only whitespace.
            return line
        return prefix + line
    lines = map(indent, lines)
    return "".join(lines)


def is_fuzzily_equal(actual, expected):
    """
    Return whether the two unicode strings are "fuzzily" equal.

    Fuzzily equal means they are equal except for ignoring ellipses final
    segments in expected.

    """
    alines, elines = (u.splitlines(True) for u in (actual, expected))

    if len(alines) != len(elines):
        return False

    for aline, eline in zip(alines, elines):
        if aline == eline:
            continue
        # Otherwise, check for ellipses in the expected line.
        i = eline.find(FUZZY_MARKER)
        if i < 0 or aline[:i] != eline[:i]:
            return False

    return True

class AssertStringMixin(object):

    """A unittest.TestCase mixin to check string equality."""

    # TODO: rename format to format_msg since it is a keyword.
    def assertString(self, actual, expected, format=None, fuzzy=False):
        """
        Assert that the given strings are equal and have the same type.

        Arguments:

          format: a function that accepts string-checking details and returns
            the desired text for the assertion failure error message.

        """
        if format is None:
            format = lambda msg: msg

        details_format = dedent("""\
        Expected: \"""%s\"""
        Actual:   \"""%s\"""

        Expected: %s
        Actual:   %s""")

        def make_message(short_description):
            # Show both friendly and literal versions.
            string_details_format = "String mismatch: %s-->\n\n%s" % (short_description, indent(details_format, "  "))
            message_format = format(string_details_format)
            message = message_format % (expected, actual, repr(expected), repr(actual))

            return message

        try:
            self.assertEqual(actual, expected, make_message("different characters"))
        except AssertionError:
            if not fuzzy or not is_fuzzily_equal(actual, expected):
                raise
            # Otherwise, ignore the exception.

        reason = "types different: %s != %s (actual)" % (repr(type(expected)), repr(type(actual)))
        self.assertEqual(type(expected), type(actual), make_message(reason))


class AssertFileMixin(AssertStringMixin):

    """A unittest.TestCase mixin to check file content equality."""

    def assertFilesEqual(self, actual_path, expected_path, format_msg=None, fuzzy=False, file_encoding='utf-8', errors='strict'):
        """
        Assert that the contents of the files at the given paths are equal.

        Arguments:

          format: a function that accepts a file details string and returns
            the desired text for the assertion failure error message.

        """
        if format_msg is None:
            format_msg = lambda msg: msg

        read = lambda path: io.read(path, encoding=file_encoding, errors=errors)

        actual, expected = (read(path) for path in (actual_path, expected_path))

        file_details_format = dedent("""\
        File contents differ at--

          Expected:  %s
          Actual:    %s

        %%s""" % (expected_path, actual_path))

        def format_string_details(string_details):
            file_details = file_details_format % indent(string_details, "  ")
            return format_msg(file_details)

        self.assertString(actual, expected, format=format_string_details, fuzzy=fuzzy)
