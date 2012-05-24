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
Unit tests for dirchooser.py.

"""

import os
import unittest

from molt.common.error import Error
from molt.dirchooser import make_output_dir
from molt.dirchooser import DirectoryChooser as Chooser
from molt.test.harness.util import make_util_load_tests


load_tests = make_util_load_tests()


class GenerateOutputDirTestCase(unittest.TestCase):

    def test_none(self):
        with self.util.sandbox_dir(self) as dir_path:
            output_dir = os.path.join(dir_path, 'foo')
            actual = make_output_dir(None, output_dir)
            self.assertEqual(output_dir, actual)

    def test_new_dir(self):
        with self.util.sandbox_dir(self) as dir_path:
            output_dir = os.path.join(dir_path, 'foo')
            actual = make_output_dir(output_dir, 'bar')
            self.assertEqual(output_dir, actual)

    def test_existing_dir(self):
        with self.util.sandbox_dir(self) as dir_path:
            output_dir = os.path.join(dir_path, 'foo')

            os.mkdir(output_dir)

            actual = make_output_dir(output_dir, 'bar')
            expected = "%s (1)" % output_dir
            self.assertEqual(expected, actual)

            # Test iterating a second time.
            actual = make_output_dir(output_dir, 'bar')
            expected = "%s (2)" % output_dir
            self.assertEqual(expected, actual)


class DirectoryChooserTestCase(unittest.TestCase):

    def _create_file(self, path):
        with open(path, 'w') as f:
            f.write('')

    def test_get_config_path__not_none(self):
        chooser = Chooser()
        actual = chooser.get_config_path('foo', 'bar')
        self.assertEqual(actual, 'foo')

    def _test_get_config_path__default(self, file_name):
        chooser = Chooser()

        with self.util.sandbox_dir(self) as dir_path:
            config_path = os.path.join(dir_path, file_name)
            self._create_file(config_path)
            actual = chooser.get_config_path(None, dir_path)
            self.assertEqual(config_path, actual)

    def test_get_config_path__no_default_exists(self):
        self.assertRaises(Error, self._test_get_config_path__default, 'random.json')

    def test_get_config_path__sample_json(self):
        self._test_get_config_path__default('sample.json')

    def test_get_config_path__sample_yaml(self):
        self._test_get_config_path__default('sample.yaml')

    def test_get_config_path__sample_yml(self):
        self._test_get_config_path__default('sample.yml')
