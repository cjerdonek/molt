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

from molt.general.dirdiff import Differ
from molt.test.harness import config_load_tests


# Trigger the load_tests protocol.
load_tests = config_load_tests

# The subdirectory of the test data directory containing the test data for
# the current module.  The path should be relative to the test data directory.
_DATA_SUB_DIR = 'dirdiff'


class DifferTestCase(unittest.TestCase):

    @property
    def _data_dir(self):
        data_dir = self.test_config.project.test_data_dir
        return os.path.join(data_dir, _DATA_SUB_DIR)

    def _assert_results(self, actual, expected):
        """
        Assert that two results containers are the same.

        """
        self.assertEquals(actual, expected)

    def test_diff(self):
        differ = Differ()
        dir1, dir2 = (os.path.join(self._data_dir, name) for name in ('dir1', 'dir2'))
        results = differ.diff(dir1, dir2)

        self._assert_results(results, (['a.txt', 'b'], ['d'], ['a/diff.txt']))

    def test_diff__directory_not_existing(self):
        differ = Differ()
        dir1, dir2 = (os.path.join(self._data_dir, name) for name in ('dir1', 'not_exist'))
        self.assertRaises(OSError, differ.diff, dir1, dir2)
