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
Exposes make_template_tests() to check template directories.

"""

# TODO: unit test this module.

from __future__ import absolute_import

from filecmp import dircmp
import logging
import os
from shutil import rmtree
from textwrap import dedent, TextWrapper
from unittest import TestCase

from pystache import Renderer

import molt
from molt.common import io
from molt.render import render
from molt.test.harness.common import test_logger as _log


TEST_FILE_ENCODING = 'utf-8'
DECODE_ERRORS = 'strict'

DIRCMP_ATTRS = ['left_only', 'right_only', 'funny_files']


# TODO: eliminate references to groom.
# TODO: accept prefix to guarantee unique directories inside the test run dir.

def make_template_tests(test_group_name, groom_input_dir, test_run_dir):
    """
    Return a list of unittest.TestCase instances.

    """
    test_case_class = _make_test_case_class(test_group_name, groom_input_dir, test_run_dir)

    # We create a closure around name using a function.  That way when
    # we iterate through the loop while changing "name", the previous
    # name value will stick with the previously defined function.
    def make_assert_template(name):
        def assert_template(test_case):
            test_case._assert_template(name)
        return assert_template

    test_cases = []
    for name in os.listdir(groom_input_dir):
        assert_template = make_assert_template(name)
        method_name = '_'.join(['test', name])
        setattr(test_case_class, method_name, assert_template)
        test_case = test_case_class(method_name)
        test_cases.append(test_case)

    return test_cases


class CompareError(Exception):
    pass


def _make_test_case_class(group_name, input_dir, test_run_dir):
    """
    Return a TemplateTestCase class with the given name.

    """
    name = "%sTemplateTestCase" % group_name
    return type(name, (TemplateTestCaseBase,),
                dict(input_dir=input_dir, test_run_dir=test_run_dir))


# The textwrap module does not expose an indent() method.
# Also see this issue: http://bugs.python.org/issue13857
def indent(text, indent_):
    lines = text.splitlines(True)
    def indent(line):
        if not line.strip():
            # Do not indent lines having only whitespace.
            return line
        return indent_ + line
    lines = map(indent, lines)
    return "".join(lines)


class TemplateTestCaseBase(TestCase):

    def get_run_output_dir(self):
        return self.test_run_dir

    def get_test_input_dir(self, template_name):
        return os.path.join(self.input_dir, template_name)

    def get_test_output_dir(self, template_name):
        run_output_dir = self.get_run_output_dir()
        return os.path.join(run_output_dir, template_name)

    def _raise_compare_error(self, expected_dir, actual_dir, details):
        details = indent(details, "  ")
        msg = """\
Directory contents differ:

  Expected | Actual :
    %s
    %s

%s

  Context: %s

Test %s: %s""" % (expected_dir, actual_dir, details, repr(self.context),
                  self.template_name, self.description)
        raise CompareError(msg)

    def _assert_empty(self, dcmp, attr_name, dirs):
        """
        Arguments:

          dcmp: a filecmp.dircmp ("directory comparison") instance.
          attr: an attribute name.
          dirs: a pair (expected_dir, actual_dir)

        """
        attr_val = getattr(dcmp, attr_name)
        if not attr_val:
            return

        expected, actual = dirs

        attr_details = "\n".join(["dircmp.%s = %s" % (attr, getattr(dcmp, attr)) for
                                  attr in DIRCMP_ATTRS])
        details = ("Attribute %s non-empty for directory compare:\n%s" %
                   (repr(attr_name), indent(attr_details, "  ")))

        self._raise_compare_error(expected, actual, details)

    def _assert_diff_files_empty(self, dcmp, expected_dir, actual_dir):
        """
        Arguments:

          dcmp: a filecmp.dircmp ("directory comparison") instance.
          expected: the expected dir.
          actual: the actual dir.

        """
        file_names = dcmp.diff_files
        if not file_names:
            return
        file_name = file_names[0]

        def read(dir_path):
            file_path = os.path.join(dir_path, file_name)
            u = io.read(file_path, encoding=TEST_FILE_ENCODING, errors=DECODE_ERRORS)
            return u

        details = dedent("""\
        Differing files: %s
        Showing first file: %s
        Expected: %s
        Actual:   %s""" % (repr(file_names), file_name,
                           repr(read(expected_dir)),
                           repr(read(actual_dir))))

        self._raise_compare_error(expected_dir, actual_dir, details)

    def _assert_dirs_equal(self, expected_dir, actual_dir):
        """
        Raise a CompareError exception if the two directories are unequal.

        """
        dirs = expected_dir, actual_dir
        dcmp = dircmp(*dirs)

        self._assert_diff_files_empty(dcmp, *dirs)
        for attr in DIRCMP_ATTRS:
            self._assert_empty(dcmp, attr, dirs)

        common_dirs = dcmp.common_dirs

        if not common_dirs:
            return

        for subdir in common_dirs:
            expected_subdir = os.path.join(expected_dir, subdir)
            actual_subdir = os.path.join(actual_dir, subdir)
            self._assert_dirs_equal(expected_subdir, actual_subdir)

    def _assert_template(self, template_name):
        """
        Arguments:

          template_name: the name of the template directory.

        """
        test_input_dir = self.get_test_input_dir(template_name)

        config_path = os.path.join(test_input_dir, 'sample.json')
        expected_dir = os.path.join(test_input_dir, 'expected')
        partials_dir = os.path.join(test_input_dir, 'partials')
        project_dir = os.path.join(test_input_dir, 'project')

        data = io.deserialize(config_path, TEST_FILE_ENCODING, DECODE_ERRORS)
        context = data['context']
        description = data['description']

        self.context = context
        self.description = description
        self.template_name = template_name

        output_dir = self.get_test_output_dir(template_name)

        os.mkdir(output_dir)
        try:
            render(project_dir, partials_dir, config_path, output_dir)
            self._assert_dirs_equal(expected_dir, output_dir)
        except BaseException:
            # Do not erase the test output if the test fails.
            raise
        else:
            rmtree(output_dir)
