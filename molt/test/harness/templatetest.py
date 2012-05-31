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
Exposes functions to create directory-rendering unittest.TestCase instances.

"""

from __future__ import absolute_import

import logging
import os
from pprint import pformat
from textwrap import dedent
from unittest import TestCase


from molt.dirchooser import make_expected_dir
from molt.molter import Molter
from molt.test.harness.common import indent
from molt.test.harness.dirmixin import AssertDirMixin
from molt.test.harness.sandbox import SandBoxDirMixin


def make_template_test(group_name, template_dir):
    names = [None]

    def make_full_name(group_name, name):
        return group_name.lower()

    def make_assert_template(group_name, name, _template_dir):
        long_name = make_full_name(group_name, name)
        expected_dir = make_expected_dir(_template_dir)

        def assert_template(test_case):
            test_case.assert_template(group_name, long_name, _template_dir, expected_dir)

        return assert_template

    test_cases = _make_template_tests(group_name, names, template_dir, make_full_name, make_assert_template)

    return test_cases[0]


def make_template_tests(group_name, parent_input_dir):
    """
    Return a list of unittest.TestCase instances.

    """
    names = os.listdir(parent_input_dir)
    # Filter out '.DS_Store'.
    names = filter(lambda dir_name: not dir_name.startswith('.'), names)

    def make_full_name(group_name, name):
        return '%s__%s' % (group_name.lower(), name)

    def make_assert_template(group_name, name, parent_input_dir):
        template_dir = os.path.join(parent_input_dir, name)
        long_name = make_full_name(group_name, name)
        expected_dir = make_expected_dir(template_dir)

        def assert_template(test_case):
            test_case.assert_template(name, long_name, template_dir, expected_dir)

        return assert_template

    return _make_template_tests(group_name, names, parent_input_dir, make_full_name,
                                make_assert_template)


def _make_template_tests(group_name, names, input_dir, make_full_name, make_assert_template):
    """
    Return a list of unittest.TestCase instances.

    """
    class_name = "%sTemplateTestCase" % group_name
    test_case_class = type(class_name, (TemplateTestCaseBase,), {})

    test_cases = []
    for name in names:
        method_name = 'test_%s' % make_full_name(group_name, name)
        assert_template = make_assert_template(group_name, name, input_dir)

        setattr(test_case_class, method_name, assert_template)

        test_case = test_case_class(method_name)
        test_cases.append(test_case)

    return test_cases


def _make_format_msg(actual_dir, expected_dir, context, test_name, test_description):
    """
    Return the format_msg function to pass to assertDirectoriesEqual().

    """
    format_string = dedent("""\
    Rendered directories differ:

      Expected | Actual :
        %s
        %s

    %%s

      Context:
    %s

    Test template info:

      Directory name: %s
      Description: %s""") % (
        expected_dir, actual_dir, indent(pformat(context), "    "),
        repr(test_name), test_description)

    def format_msg(details):
        msg = format_string % indent(details, "  ")
        return msg

    return format_msg


class TemplateTestCaseBase(TestCase, AssertDirMixin, SandBoxDirMixin):

    def assert_template(self, template_name, long_name, template_dir, expected_dir):
        """
        Arguments:

          template_name: the name of the template directory.

          input_dir: the directory containing the project directory,
            partials directory, and config file.

        """
        molter = Molter()

        config = molter.read_config(template_dir)
        context = molter.get_context(template_dir)
        description = config['description']

        with self.sandboxDir() as actual_dir:
            molter.molt(template_dir=template_dir, output_dir=actual_dir)
            format_msg = _make_format_msg(actual_dir, expected_dir, context=context,
                                          test_name=template_name,
                                          test_description=description)
            self.assertDirectoriesEqual(actual_dir, expected_dir, fuzzy=True,
                                        format_msg=format_msg)
