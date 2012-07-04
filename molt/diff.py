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

from molt.defaults import FUZZY_MARKER


_log = logging.getLogger(__name__)

# TODO: expose a wrapper function for comparing directories that accepts
#   a fuzzy argument.  It should internally call dirdiff.Differ.diff().

def are_fuzzy_equal(u1, u2, marker=None):
    """
    Return whether the two unicode strings are "fuzzily" equal.

    Fuzzily equal means they are equal except for ignoring ellipses final
    segments in the second argument.

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
