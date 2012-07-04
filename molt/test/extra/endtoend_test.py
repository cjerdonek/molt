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
Provides end-to-end tests that call Molt from the command-line.

"""

import logging
import os
import sys
from unittest import TestCase

from molt.common.popen import call_script
from molt.test.harness import (
    config_load_tests,
    should_ignore_file,
    AssertDirMixin,
    SandBoxDirMixin,
)


ENCODING_DEFAULT = 'utf-8'

_log = logging.getLogger(__name__)


# Trigger the load_tests protocol.
load_tests = config_load_tests


def _call_script(args):
    stdout, stderr, return_code = call_script(args)

    stdout, stderr = (s.decode(ENCODING_DEFAULT) for s in (stdout, stderr))

    return stdout, stderr, return_code


def _call_python_script(args):
    """
    Call `python` from the command-line.

    """
    python_path = sys.executable
    args = [python_path] + args
    stdout, stderr, return_code = _call_script(args)

    return args, stdout, stderr, return_code


class EndToEndMixin(SandBoxDirMixin, AssertDirMixin):

    """
    Mixin class for TestCase classes in this module.

    """

    @property
    def _demo_template_dir(self):
        return self.test_config.project.demo_template_dir

    def _call_molt(self, args):
        """
        Call `molt` from the command-line.

        """
        first_args = self.test_config.call_molt_args
        args = first_args + args

        stdout, stderr, return_code = _call_script(args)

        return args, stdout, stderr, return_code

    def make_format_message(self, args, stderr):
        """
        Return a format_msg(details) function for assertion failures.

        """
        def format_msg(details):
            msg = "%s\n-->stderr from command-line call: %s\n--->%s" % (details,
                repr(" ".join(args)), stderr)
            return msg
        return format_msg

    def assert_call(self, call_func, args, expected_stdout):
        """
        Call the given command-line calling function and assert the outcome.

        Arguments:

          call_func: a function that accepts args and returns a tuple
            (args, stdout, stderr, return_code).

          expected_stdout: a unicode string.

        Returns (args, stderr).

        """
        args, stdout, stderr, return_code = call_func(args)

        format_msg = self.make_format_message(args, stderr)

        self.assertEquals(0, return_code, msg=format_msg("exit status: %s != 0" % return_code))
        self.assertEquals(stdout.strip(), expected_stdout)

        return args, stderr

    def assert_python(self, args, expected_stdout):
        """
        Call a Python script from the command-line and assert the outcome.

        """
        self.assert_call(_call_python_script, args, expected_stdout)

    def assert_molt(self, args, actual_dir, expected_dir, expected_stdout, fuzzy=False):
        """
        Call molt from the command-line and assert the outcome.

        """
        args, stderr = self.assert_call(self._call_molt, args, expected_stdout)

        format_msg = self.make_format_message(args, stderr)

        self.assertDirectoriesEqual(actual_dir, expected_dir, format_msg=format_msg, fuzzy=fuzzy,
                                    should_ignore=should_ignore_file)


class ReadmeTestCase(TestCase, EndToEndMixin):

    """
    Tests the instructions given in the README.

    """

    def test_try_it(self):
        """
        Test the instructions in the "Try it" section of the README.

        """
        with self.sandboxDir() as temp_dir:
            demo_dir = os.path.join(temp_dir, 'demo')
            # Test creating the demo.
            output_dir = demo_dir
            args = ['--create-demo', '--output', output_dir]
            self.assert_molt(args, output_dir, expected_dir=self._demo_template_dir,
                             expected_stdout=output_dir)

            # Test rendering the demo.
            output_dir = os.path.join(temp_dir, 'output')
            config_path = os.path.join(demo_dir, 'sample.json')
            args = ['--output', output_dir, '--config', config_path, demo_dir]
            expected_dir = os.path.join(demo_dir, 'expected')
            self.assert_molt(args, output_dir, expected_dir=expected_dir,
                             expected_stdout=output_dir, fuzzy=True)

            # Test executing the rendered project.
            main_path = os.path.join(output_dir, 'hello.py')
            args = [main_path, 'world']
            self.assert_python(args, "Hello, world!")


class CreateDemoTestCase(TestCase, EndToEndMixin):

    def test_create_demo__with_output(self):
        with self.sandboxDir() as temp_dir:
            output_dir = os.path.join(temp_dir, 'demo')
            args = ['--create-demo', '--output', output_dir]

            actual_dir = output_dir
            expected_dir = self._demo_template_dir

            self.assert_molt(args, output_dir, expected_dir=expected_dir,
                             expected_stdout=output_dir)
