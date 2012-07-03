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
Unit tests for dirutil.py.

"""

import os
import unittest

from molt.common.error import Error
from molt.common.popen import call_script
from molt.dirutil import make_available_dir, set_executable_bit
from molt.dirutil import DirectoryChooser as Chooser
from molt.test.harness import config_load_tests, SandBoxDirMixin


# We want a shebang line that will work on the maximum number of systems.
SHEBANG_LINE = "#!/bin/sh\n"

load_tests = config_load_tests


# TODO: share code with common/io.
def _create_file(path, text=''):
    with open(path, 'w') as f:
        f.write(text)


class MakeAvailableDirTestCase(unittest.TestCase, SandBoxDirMixin):

    def test_new_dir(self):
        with self.sandboxDir() as dir_path:
            output_dir = os.path.join(dir_path, 'foo')
            actual = make_available_dir(output_dir)
            self.assertEqual(output_dir, actual)

    def test_existing_dir(self):
        with self.sandboxDir() as dir_path:
            output_dir = os.path.join(dir_path, 'foo')

            os.mkdir(output_dir)

            actual = make_available_dir(output_dir)
            expected = "%s_1" % output_dir
            self.assertEqual(expected, actual)

            # Test iterating a second time.
            actual = make_available_dir(output_dir)
            expected = "%s_2" % output_dir
            self.assertEqual(expected, actual)


class SetExecutableBitTestCase(unittest.TestCase, SandBoxDirMixin):

    def test(self):
        with self.sandboxDir() as dir_path:
            path = os.path.join(dir_path, "test.sh")
            _create_file(path, SHEBANG_LINE)
            args = [path]

            # Will not work until we set the executable bit.
            # TODO: switch from Exception to OSError.  We cannot do this
            #   until we've changed our implementation of reraise() to
            #   preserve the exception type.
            self.assertRaises(Exception, call_script, args)
            set_executable_bit(path)
            stdout_data, stderr_data, return_code = call_script(args)


class DirectoryChooserTestCase(unittest.TestCase, SandBoxDirMixin):

    def _assert_config_path(self):
        chooser = Chooser()
        config_path = os.path.join(dir_path, file_name)
        _create_file(config_path)
        actual = chooser.get_config_path(None, dir_path)
        self.assertEqual(config_path, actual)

    def test_get_config_path__not_none(self):
        chooser = Chooser()
        actual = chooser.get_config_path('foo', 'bar')
        self.assertEqual(actual, 'foo')

    def _test_get_config_path__default(self, file_name, assert_func):
        """
        Arguments:

          file_name: the name of the file to create in the template directory
            prior to making any assertions.

          assert_func: a function of (chooser, expected_path, template_dir)
            that makes an assertion about chooser.get_config_path(None, template_dir).

        """
        chooser = Chooser()

        with self.sandboxDir() as template_dir:
            config_path = os.path.join(template_dir, file_name)
            _create_file(config_path)
            assert_func(chooser, config_path, template_dir)

    def _test_get_config_path__default__exists(self, file_name):
        """
        Test that the given file name is recognized as a default

        """
        def assert_func(chooser, config_path, template_dir):
            actual = chooser.get_config_path(None, template_dir)
            self.assertEqual(config_path, actual)

        self._test_get_config_path__default(file_name, assert_func)

    def test_get_config_path__no_default(self):
        """
        Test what happens when none of the recognized defaults exist.

        """
        def assert_func(chooser, config_path, template_dir):
            self.assertRaises(Error, chooser.get_config_path, None, template_dir)

        self._test_get_config_path__default('random.json', assert_func)

    def test_get_config_path__sample_json(self):
        self._test_get_config_path__default__exists('sample.json')

    def test_get_config_path__sample_yaml(self):
        self._test_get_config_path__default__exists('sample.yaml')

    def test_get_config_path__sample_yml(self):
        self._test_get_config_path__default__exists('sample.yml')
