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
Provides end-to-end tests that exercise molt from the command-line.

"""

import logging
import os
import sys
from unittest import TestCase

from molt.common.popen import call_script
from molt.constants import DEMO_TEMPLATE_DIR
from molt.test.harness.loading import config_load_tests
from molt.test.harness.sandbox import SandBoxDirMixin


# Trigger the load_tests protocol.
load_tests = config_load_tests


class EndToEndTestCase(TestCase, SandBoxDirMixin):

    def _call_molt(self, args):
        python_path = sys.executable
        args = [python_path, '-m', 'molt.commands.molt'] + args
        stdout, stderr = call_script(args)

        return stdout, stderr

    def test_create_demo__with_output(self):
        with self.sandboxDir() as temp_dir:
            output_dir = os.path.join(temp_dir, 'demo')
            options = ['--create-demo', '--output', output_dir]
            stdout, stderr = self._call_molt(options)
            self.assertEquals(stdout.strip(), output_dir)
