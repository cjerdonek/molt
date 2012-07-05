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
import os
from textwrap import dedent

from molt.diff import match_fuzzy, FileComparer
from molt.general import io
import molt.test


test_logger = logging.getLogger(molt.test.__name__)


# The textwrap module does not expose an indent() method.
# Also see this issue: http://bugs.python.org/issue13857
def indent(text, prefix):
    lines = text.splitlines(True)
    def _indent(line):
        if not line.strip():
            # Do not indent lines having only whitespace.
            return line
        return prefix + line
    lines = map(_indent, lines)
    return "".join(lines)


def _make_message(actual, expected, format_msg, description=None):
    """
    Return the text to pass as the msg argument to a self.assert*() method.

    """
    def new_format_msg(details):
        new_details = dedent("""\
        %s-->

        %s""") % (description, indent(details, "  "))

        return format_msg(new_details)

    # Show both friendly and literal versions.
    string_details_format = dedent("""\
    EXPECTED: \"""%s\"""
    ACTUAL:   \"""%s\"""

    EXPECTED: %s
    ACTUAL:   %s
    """)

    message_format = new_format_msg(string_details_format)

    # TODO: escape message_format prior to doing the following string
    #   interpolation.
    #
    # We do string interpolation at the very end to prevent the literal
    # version of each string from being indented.  We want the second
    # and subsequent lines to be left-justified to simplify cutting
    # and pasting.
    message = message_format % (expected, actual, repr(expected), repr(actual))

    return message


class AssertStringMixin(object):

    """A unittest.TestCase mixin to check string equality."""

    def __assertStringMatch(self, actual, expected, format_msg):
        """
        Assert that the given strings are equal and have the same type.

        """
        def make_description(info):
            return "Strings not equal: %s" % info

        description = make_description("different characters")
        msg = _make_message(actual, expected, format_msg, description=description)
        self.assertEqual(actual, expected, msg=msg)

        info = "types different: %s != %s (actual)" % (repr(type(expected)), repr(type(actual)))
        description = make_description(info)
        msg = _make_message(actual, expected, format_msg, description=description)
        self.assertEqual(type(expected), type(actual), msg=msg)

    def assertFuzzy(self, actual, expected, format_msg=None):
        """
        Assert that two unicode strings are fuzzily equal.

        """
        if format_msg is None:
            format_msg = lambda msg: msg

        description = "Strings do not match fuzzily"
        msg = _make_message(actual, expected, format_msg, description=description)

        self.assertTrue(match_fuzzy(actual, expected), msg=msg)

    def assertString(self, actual, expected, format_msg=None, fuzzy=False):
        """
        Assert that the given strings match.

        Arguments:

          format_msg: a function that accepts a details string and returns
            the text to pass as the msg argument to a unittest
            self.assert*() method.

        """
        if format_msg is None:
            format_msg = lambda msg: msg

        assert_func = self.assertFuzzy if fuzzy else self.__assertStringMatch

        assert_func(actual, expected, format_msg=format_msg)


class AssertFileMixin(AssertStringMixin):

    """A unittest.TestCase mixin to check file content equality."""

    def assertFileExists(self, path, label=None, format_msg=None):
        if format_msg is None:
            format_msg = lambda msg: msg

        label = "path" if label is None else label
        msg = format_msg("%s does not exist: %s" % (label, path))
        self.assertTrue(os.path.exists(path), msg=msg)

    def assertFilesEqual(self, actual_path, expected_path, format_msg=None,
                         fuzzy=False, file_encoding='utf-8', errors='strict'):
        """
        Assert that the contents of the files at the given paths are equal.

        Arguments:

          format_msg: a function that accepts a details string and returns
            the text to pass as the msg argument to a unittest
            self.assert*() method.

        """
        if format_msg is None:
            format_msg = lambda msg: msg

        match_func = match_fuzzy if fuzzy else None

        fcmp = FileComparer(actual_path, expected_path, match=match_func)
        actual_match = fcmp.compare()

        def new_format_msg(details):
            new_details = dedent("""\
            File contents don't match (fuzzy=%s) at--

              Expected:  %s
              Actual:    %s

            %s""") % (fuzzy, expected_path, actual_path, indent(details, "  "))

            return format_msg(new_details)

        description = "Displaying file contents"
        msg = _make_message(fcmp.left, fcmp.right, format_msg=new_format_msg,
                            description=description)

        self.assertTrue(actual_match, msg=msg)
