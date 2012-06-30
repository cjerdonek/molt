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

import os
from pprint import pformat
from textwrap import dedent
from unittest import TestCase


from molt.dirutil import make_expected_dir, stage_template_dir
from molt.molter import Molter
from molt.test.harness import indent, should_ignore_file, AssertDirMixin, SandBoxDirMixin


def make_test_class_type_args(group_name, template_dir, should_stage=False):
    """
    Return a type args triple for a unittest.TestCase subclass.

    """
    names = [None]

    def make_full_name(group_name, name):
        return group_name.lower()

    def make_assert_template(group_name, name, _template_dir):
        long_name = make_full_name(group_name, name)
        expected_dir = make_expected_dir(_template_dir)

        def assert_template(test_case):
            test_case.assert_template(group_name, long_name, _template_dir, expected_dir,
                                      should_stage=should_stage)

        return assert_template

    type_args = _make_test_case_type_args(group_name, names, template_dir, make_full_name,
                                          make_assert_template)

    return type_args

def make_template_tests_class(group_name, parent_input_dir):
    """
    Return a type args triple for a unittest.TestCase subclass.

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

    type_args = _make_test_case_type_args(group_name, names, parent_input_dir, make_full_name,
                                          make_assert_template)
    return type_args


def _make_test_case_type_args(group_name, names, input_dir, make_full_name, make_assert_template):
    """
    Return the type info for a TestCase subclass containing template tests.

    Returns a triple usable as the arguments for type(): (name, bases, dict).

    """
    class_name = "%sTemplateTestCase" % group_name

    test_methods = {}
    for name in names:
        method_name = 'test_%s' % make_full_name(group_name, name)
        assert_template = make_assert_template(group_name, name, input_dir)

        test_methods[method_name] = assert_template

    return class_name, (TemplateTestCaseBase,), test_methods


def _make_format_msg(actual_dir, expected_dir, context, test_name, test_description):
    """
    Return the format_msg function to pass to assertDirectoriesEqual().

    """
    # TODO: review the relationship between "directory name" and "test name".
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

    def assert_template(self, template_name, long_name, template_dir, expected_dir,
                        should_stage=False):
        """
        Arguments:

          template_name: the short name for the template.

          template_dir: the directory containing the lambdas directory,
            partials directory, etc.

          should_stage: whether to stage the template directory.  This option
            is useful, for example, if the executable bit is not set on the
            lambda scripts in the original template lambdas directory.

        """
        molter = Molter()

        with self.sandboxDir() as temp_dir:
            actual_dir = os.path.join(temp_dir, 'actual')
            os.mkdir(actual_dir)

            if should_stage:
                staged_template_dir = os.path.join(temp_dir, 'template')
                stage_template_dir(template_dir, staged_template_dir)
                template_dir = staged_template_dir

            context = molter.get_context(template_dir)
            config = molter.read_config(template_dir)
            description = config['description']

            molter.molt(template_dir=template_dir, output_dir=actual_dir)
            format_msg = _make_format_msg(actual_dir, expected_dir, context=context,
                                          test_name=template_name,
                                          test_description=description)
            self.assertDirectoriesEqual(actual_dir, expected_dir, fuzzy=True,
                                        format_msg=format_msg,
                                        should_ignore=should_ignore_file)
