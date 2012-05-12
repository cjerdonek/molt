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

from filecmp import dircmp
import os
import unittest

from pystache import Renderer

import molt
from molt.common import io
from molt.render import preprocess_filename, Molter


ENCODING = 'utf-8'
DECODE_ERRORS = 'strict'

SOURCE_DIR = os.path.dirname(molt.__file__)
TEMPLATES_DIR = os.path.join(SOURCE_DIR, os.path.normpath('test/data/templates'))


class CompareError(Exception):
    pass


def assert_false(c, attr, dir_path):
    """
    Arguments:

      c: a filecmp.dircmp instance.
      attr: an attribute name.

    """
    val = getattr(c, attr)
    if not val:
        return
    raise CompareError("non-empty %s for %s: %s" % (attr, dir_path, val))

def assert_dirs_equal(expected_dir, actual_dir):
    """
    Raise a CompareError exception if the two directories are unequal.

    """
    c = dircmp(expected_dir, actual_dir)

    assert_false(c, 'left_only', expected_dir)
    assert_false(c, 'right_only', expected_dir)
    assert_false(c, 'diff_files', expected_dir)
    assert_false(c, 'funny_files', expected_dir)

    common_dirs = c.common_dirs

    if not common_dirs:
        return

    for subdir in common_dirs:
        expected_subdir = os.path.join(expected_dir, subdir)
        actual_subdir = os.path.join(actual_dir, subdir)
        assert_dirs_equal(expected_subdir, actual_subdir)


class PreprocessFileNameTestCase(unittest.TestCase):

    """Test preprocess_filename()."""

    def _assert(self, input, expected):
        self.assertEqual(preprocess_filename(input), expected)

    def test(self):
        self._assert('README.md', ('README.md', False))
        self._assert('README.md.mustache', ('README.md', True))
        self._assert('README.skip.mustache', ('README.mustache', False))


class TemplateTestCase(unittest.TestCase):

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
        data = data['context']

        renderer = Renderer()
        molter = Molter(renderer)

        output_dir = 'output'

        #os.mkdir(output_dir)
        #molter.molt_dir(template_dir, data, output_dir)

        assert_dirs_equal(expected_dir, output_dir)


for name in os.listdir(TEMPLATES_DIR):
    def assert_template(test_case):
        test_case._assert_template(name)

    setattr(TemplateTestCase, '_'.join(['test', name]), assert_template)
