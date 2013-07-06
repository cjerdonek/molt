# encoding: utf-8
#
# Copyright (C) 2011-2012 Chris Jerdonek. All rights reserved.
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
Unit tests for dirdiff.py.

"""

from __future__ import absolute_import

import os
import unittest

# TODO: remove the molt.defaults and molt.diff import dependencies.
from molt.defaults import DIRCMP_IGNORE
from molt.diff import match_fuzzy
from molt.general.dirdiff import compare_files, DirComparer
import molt.general.dirdiff as dirdiff
from molt.test.harness import config_load_tests


# Trigger the load_tests protocol.
load_tests = config_load_tests

# The subdirectory of the test data directory containing the test data for
# the current module.  The path should be relative to the test data directory.
_DATA_SUB_DIR = 'dirdiff'

# The subdirectory of the test data directory containing the test data for
# MatchFilesTestCase.  The path is relative to the test data directory.
_MATCH_FILES_DIR = 'diff__FileComparer'


class FileComparerTestCase(unittest.TestCase):

    @property
    def _data_dir(self):
        data_dir = self.test_config.project.test_data_dir
        return os.path.join(data_dir, _MATCH_FILES_DIR)

    def _assert(self, file_name1, file_name2, expected, match_func=None):
        """
        Assert whether the contents of the two files match.

        """
        path1, path2 = (os.path.join(self._data_dir, name) for name in (file_name1, file_name2))

        fcmp = dirdiff.FileComparer(match=match_func)
        actual = fcmp.compare(path1, path2)

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


class DirComparerTestCase(unittest.TestCase):

    @property
    def _data_dir(self):
        data_dir = self.test_config.project.test_data_dir
        return os.path.join(data_dir, _DATA_SUB_DIR)

    def _assert_results(self, actual, expected):
        """
        Assert that two results containers are the same.

        """
        # TODO: make this check OS-independent (with respect to paths).
        self.assertEquals(actual, expected)

    def _assert_diff(self, expected, compare=None):
        differ = DirComparer(compare=compare, ignore=DIRCMP_IGNORE)
        dir1, dir2 = (os.path.join(self._data_dir, name) for name in ('dir1', 'dir2'))
        actual = differ.diff(dir1, dir2)

        self._assert_results(actual, expected)

    def test_diff__basic(self):
        expected = (['a.txt', 'b'], ['d'], ['a/diff.txt', 'a/diff2.txt'])
        self._assert_diff(expected=expected)

    def test_diff__compare__default(self):
        """
        Check that passing dirdiff.compare_files works as expected.

        """
        expected = (['a.txt', 'b'], ['d'], ['a/diff.txt', 'a/diff2.txt'])
        self._assert_diff(expected=expected, compare=compare_files)

    def test_diff__compare__fuzzy(self):
        """
        Check that the compare argument works for a basic "fuzzy" example.

        This test also checks that even same files are checked again
        using the custom compare function (since "same.txt" is included
        in the list of differences).

        """
        expected = (['a.txt', 'b'], ['d'], ['a/same.txt'])
        compare = lambda path1, path2: os.path.basename(path1).startswith('diff')

        self._assert_diff(expected=expected, compare=compare)

    def test_diff__compare__stricter(self):
        """
        Check that compare works for something stricter than the default.

        """
        expected = (['a.txt', 'b'], ['d'], ['a/diff.txt', 'a/diff2.txt', 'a/same.txt'])
        # The strictest possible compare function returns False for every comparison.
        compare = lambda path1, path2: False

        self._assert_diff(expected=expected, compare=compare)

    def test_diff__directory_not_existing(self):
        differ = DirComparer()
        dir1, dir2 = (os.path.join(self._data_dir, name) for name in ('dir1', 'not_exist'))
        self.assertRaises(OSError, differ.diff, dir1, dir2)
