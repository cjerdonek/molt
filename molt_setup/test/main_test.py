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
Unit tests for the main module.

"""

import os
from unittest import TestCase

import molt_setup
from molt_setup.main import (
    describe_difference,
    find_package_data,
    make_temp_path,
    walk_dir,
)


setup_dir = os.path.dirname(molt_setup.__file__)
PACKAGE_DIR = os.path.join(setup_dir, 'test', 'data', 'package_dir')


def assert_paths_equal(test_case, actual_paths, expected_paths):
    normalize = lambda paths: [os.path.normpath(path) for path in paths]

    actual, expected = normalize(actual_paths), normalize(expected_paths)

    test_case.assertEquals(actual, expected)


class MakeTempPathTestCase(TestCase):

    def test_txt(self):
        actual = make_temp_path('foo.txt')
        self.assertEquals(actual, 'foo.temp.txt')

    def test_rst(self):
        actual = make_temp_path('foo.rst')
        self.assertEquals(actual, 'foo.temp.rst')

    def test_new_ext(self):
        actual = make_temp_path('foo.rst', new_ext='.txt')
        self.assertEquals(actual, 'foo.temp.txt')


class WalkDirTestCase(TestCase):

    def test_walk_dir(self):
        top_dir = PACKAGE_DIR

        actual = walk_dir(top_dir)
        assert_paths_equal(self, actual, ['foo', 'foo/bar', 'foo/bar/foo.txt', 'foo/foo.txt'])

    def test_find_dirs(self):
        top_dir = PACKAGE_DIR

        actual = walk_dir(top_dir, exclude_files=True)
        assert_paths_equal(self, actual, ['foo', 'foo/bar'])


class FindPackageDataTestCase(TestCase):

    def test(self):
        root_dir = PACKAGE_DIR
        self.assertTrue(os.path.isdir(root_dir), msg="Not found: %s" % root_dir)

        actual = find_package_data(root_dir, 'foo', ['*.txt'])
        assert_paths_equal(self, actual, ['foo/*.txt', 'foo/bar/*.txt'])
