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
Provides end-to-end tests that exercise Molt from the command-line.

"""

import logging
import os
import sys
from unittest import TestCase

import molt.commands.molt
from molt.common.popen import call_script
from molt.constants import DEMO_TEMPLATE_DIR
from molt.test.harness import config_load_tests, AssertDirMixin, SandBoxDirMixin

_log = logging.getLogger(__name__)


# Trigger the load_tests protocol.
load_tests = config_load_tests


def _call_molt(args):
    """
    Call molt using the command-line.

    """
    python_path = sys.executable
    args = [python_path, '-m', molt.commands.molt.__name__] + args
    stdout, stderr, return_code = call_script(args)

    return stdout, stderr, return_code


class ReadmeTestCase(TestCase, SandBoxDirMixin, AssertDirMixin):

    """
    Tests the instructions given in the README.

    """

    def _assert_molt(self, args, actual_dir, expected_dir, expected_output, fuzzy=False):
        """
        Call molt from the command-line and assert the outcome.

        """
        stdout, stderr, return_code = _call_molt(args)

        def format_msg(details):
            msg = "%s\n-->stderr from molt call: %s\n--->%s" % (details,
                repr(" ".join(args)), stderr)
            return msg

        self.assertEquals(0, return_code, msg=format_msg("exit status: %s != 0" % return_code))
        self.assertDirectoriesEqual(actual_dir, expected_dir, format_msg=format_msg, fuzzy=fuzzy)
        self.assertEquals(stdout.strip(), expected_output)

    def test_try_it(self):
        """
        Test the instructions in the "Try it" section of the README.

        """
        with self.sandboxDir() as temp_dir:
            demo_dir = os.path.join(temp_dir, 'demo')
            # Test creating the demo.
            output_dir = demo_dir
            args = ['--create-demo', '--output', output_dir]
            self._assert_molt(args, output_dir, expected_dir=DEMO_TEMPLATE_DIR,
                              expected_output=output_dir)

            # Test rendering the demo.
            output_dir = os.path.join(temp_dir, 'output')
            config_path = os.path.join(demo_dir, 'sample.json')
            args = ['--output', output_dir, '--config', config_path, demo_dir]
            expected_dir = os.path.join(demo_dir, 'expected')
            self._assert_molt(args, output_dir, expected_dir=expected_dir,
                              expected_output=output_dir, fuzzy=True)


# TODO: share subclass and leverage self._assert_molt().
class EndToEndTestCase(TestCase, SandBoxDirMixin, AssertDirMixin):

    def test_create_demo__with_output(self):
        with self.sandboxDir() as temp_dir:
            output_dir = os.path.join(temp_dir, 'demo')
            options = ['--create-demo', '--output', output_dir]
            stdout, stderr, return_code = _call_molt(options)

            actual_dir = output_dir
            expected_dir = DEMO_TEMPLATE_DIR

            self.assertDirectoriesEqual(actual_dir, expected_dir)
            self.assertEquals(stdout.strip(), output_dir)
