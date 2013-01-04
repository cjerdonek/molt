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
Supports Molt-specific file and directory diff functionality.

"""

from __future__ import absolute_import

import logging
import os
import sys

from molt.defaults import FILE_ENCODING, FUZZY_MARKER
from molt.general.dirdiff import compare_files, DirDiffer
from molt.general.io import read


_ENCODING = FILE_ENCODING

_log = logging.getLogger(__name__)



# TODO: think about providing more than just the true/false information
#   of whether two strings are equal in these methods.  For example, one
#   could provide line and character number, and/or surrounding context.
#   Study the difflib module more closely:
#     http://docs.python.org/library/difflib.html#module-difflib)
#   though it may be hard to leverage because of our need to support
#   fuzzy matching.

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

class FileComparer(object):

    def __init__(self, match=None):
        """
        Arguments:

          match: a function that accepts two unicode strings, and returns
            whether they should be considered equal.  Defaults to the
            usual string equality operator.

        """
        if match is None:
            match = unicode.__eq__

        self.match_func = match

    def compare(self, path1, path2):
        _read = lambda path: read(path, encoding=_ENCODING, errors=_ENCODING)

        self.left, self.right = map(_read, (path1, path2))

        return self.match_func(self.left, self.right)
