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
TODO: add a docstring.

"""

from __future__ import absolute_import

import os
from shutil import copyfile
import unittest

from molt.general.popen import call_script
from molt.dirutil import set_executable_bit
from molt.test.harness import config_load_tests, SandBoxDirMixin
from molt.test.harness.common import AssertStringMixin


ENCODING_DEFAULT = 'utf-8'


# Trigger the load_tests protocol.
load_tests = config_load_tests


class CallScriptTestCase(unittest.TestCase, AssertStringMixin, SandBoxDirMixin):

    # Override unittest.TestCase.run() to use the sandbox directory
    # context manager for all test methods.  Using setUp() and tearDown()
    # is inelegant and more difficult.  See--
    #
    #   http://stackoverflow.com/questions/8416208/in-python-is-there-a-good-idiom-for-using-context-managers-in-setup-teardown
    #
    def run(self, result=None):
        with self.sandboxDir() as temp_dir:
            self.temp_dir = temp_dir
            super(CallScriptTestCase, self).run(result)

    def _get_script_path(self, script_name):
        data_dir = self.test_config.project.test_data_dir
        return os.path.join(data_dir, 'lambdas', script_name + ".sh")

    def _call_script(self, script_name, u):
        """
        Return stdout as a unicode string.

        """
        script_path = self._get_script_path(script_name)

        base_name = os.path.basename(script_path)
        new_path = os.path.join(self.temp_dir, base_name)

        copyfile(script_path, new_path)
        set_executable_bit(new_path)

        bytes_in = u.encode(ENCODING_DEFAULT)

        stdout, stderr, return_code = call_script([new_path], bytes_in)

        stdout = stdout.decode(ENCODING_DEFAULT)

        return stdout

    def test_echo_string(self):
        """
        Test calling a script that echoes a constant string.

        """
        self.assertEqual('foo', self._call_script('echo_foo', ''))

    def test_hash_comment(self):
        script_name = 'hash_comment'

        actual = self._call_script(script_name, '')
        expected = u''
        self.assertString(actual, expected)

        actual = self._call_script(script_name, 'line1\nline2')
        expected = u'# line1\n'
        self.assertString(actual, expected)

        actual = self._call_script(script_name, 'line1\nline2\n')
        expected = u'# line1\n# line2\n'
        self.assertString(actual, expected)

        actual = self._call_script(script_name, 'line1\nline2\n\n')
        expected = u'# line1\n# line2\n# \n'
        self.assertString(actual, expected)
