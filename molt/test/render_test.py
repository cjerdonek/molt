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
Unit tests for render.py.

"""

from datetime import datetime
from filecmp import dircmp
import os
from textwrap import dedent, TextWrapper
import unittest

from pystache import Renderer

import molt
from molt.common import io
from molt.render import preprocess_filename, Molter


ENCODING = 'utf-8'
DECODE_ERRORS = 'strict'

DIRCMP_ATTRS = ['left_only', 'right_only', 'funny_files']

SOURCE_DIR = os.path.dirname(molt.__file__)
PROJECT_DIR = os.path.normpath(os.path.join(SOURCE_DIR, os.pardir))
TEMP_DIR = 'temp'
TEMPLATES_DIR = os.path.join(PROJECT_DIR, os.path.normpath('submodules/groom/tests'))


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


class CompareError(Exception):
    pass


class PreprocessFileNameTestCase(unittest.TestCase):

    """Test preprocess_filename()."""

    def _assert(self, input, expected):
        self.assertEqual(preprocess_filename(input), expected)

    def test(self):
        self._assert('README.md', ('README.md', False))
        self._assert('README.md.mustache', ('README.md', True))
        self._assert('README.skip.mustache', ('README.mustache', False))


class TemplateTestCase(unittest.TestCase):

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
            u = io.read(file_path, encoding=ENCODING, errors=DECODE_ERRORS)
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
        test_dir = os.path.join(TEMPLATES_DIR, template_name)

        template_dir = os.path.join(test_dir, 'template')
        config_path = os.path.join(test_dir, 'sample.json')
        expected_dir = os.path.join(test_dir, 'expected')

        data = io.deserialize(config_path, ENCODING, DECODE_ERRORS)
        context = data['context']
        description = data['description']

        self.context = context
        self.description = description
        self.template_name = template_name

        renderer = Renderer(file_encoding=ENCODING)
        molter = Molter(renderer)

        output_dir = os.path.join(TEST_RUN_DIR, template_name)

        os.mkdir(output_dir)
        molter.molt_dir(template_dir, context, output_dir)

        self._assert_dirs_equal(expected_dir, output_dir)


def make_assert_template(name):
    def assert_template(test_case):
        test_case._assert_template(name)
    return assert_template


for name in os.listdir(TEMPLATES_DIR):
    assert_template = make_assert_template(name)
    setattr(TemplateTestCase, '_'.join(['test', name]), assert_template)


if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)

# TODO: allow configuring deletion of the test directory.
while True:
    dt = datetime.now()
    dir_name = "test_run_%s" % dt.strftime("%Y%m%d-%H%M%S")
    dir_path = os.path.join(TEMP_DIR, dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        break

TEST_RUN_DIR = dir_path
