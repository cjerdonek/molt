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
import unittest

from molt.common.popen import call_script
from molt.constants import TEST_DATA_DIR
from molt.test.harness.common import AssertStringMixin

class CallScriptTestCase(unittest.TestCase, AssertStringMixin):

    def _get_script_path(self, script_name):
        return os.path.join(TEST_DATA_DIR, 'lambdas', script_name + ".sh")

    def _call_script(self, path, bytes_in):
        stdout, stderr, return_code = call_script([path], bytes_in)
        return stdout

    def test_constant(self):
        """
        Test calling a script that echoes a constant.

        """
        path = self._get_script_path('foo')
        self.assertEqual('bar', self._call_script(path, ''))

    def test_hash_comment(self):
        path = self._get_script_path('hash_comment')

        actual = self._call_script(path, '')
        expected = ''
        self.assertString(actual, expected)

        actual = self._call_script(path, 'line1\nline2')
        expected = '# line1\n'
        self.assertString(actual, expected)

        actual = self._call_script(path, 'line1\nline2\n')
        expected = '# line1\n# line2\n'
        self.assertString(actual, expected)

        actual = self._call_script(path, 'line1\nline2\n\n')
        expected = '# line1\n# line2\n# \n'
        self.assertString(actual, expected)
