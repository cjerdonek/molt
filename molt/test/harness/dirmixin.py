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
Exposes a unittest.TestCase mixin for verifying directory contents.

"""

from __future__ import absolute_import

from filecmp import dircmp
import os
from textwrap import dedent

from molt.test.harness import indent
from molt.test.harness.common import AssertFileMixin


TEST_FILE_ENCODING = 'utf-8'
DECODE_ERRORS = 'strict'

DIRCMP_ATTRS = ['left_only', 'right_only', 'funny_files']

# TODO: inject this value at run-time using load_tests().
SKIPPED_FILES = ['.DS_Store']


class AssertDirMixin(AssertFileMixin):

    """
    A unittest.TestCase mixin for checking directory content equality.

    """

    def _make_subdir_format_msg(self, actual_dir, expected_dir, format_msg):
        """
        Return the format_msg function to use for a subdirectory difference.

        """
        format_string = dedent("""\
        Subdirectories differ:

          Expected | Actual :
            %s
            %s

        %%s""") % (expected_dir, actual_dir)

        def subdir_format_msg(subdir_details):
            details = format_string % indent(subdir_details, "  ")
            return format_msg(details)

        return subdir_format_msg

    def _get_dirs(self, dcmp):
        """
        Return (expected_dir, actual_dir) from a dircmp instance.

        """
        expected_dir, actual_dir = dcmp.left, dcmp.right
        return expected_dir, actual_dir

    def _get_dcmp_attr(self, dcmp, attr_name):
        attr_val = getattr(dcmp, attr_name)
        attr_val = filter(lambda file_name: file_name not in SKIPPED_FILES, attr_val)

        return attr_val

    def _assert_empty(self, dcmp, attr_name, format_msg):
        """
        Arguments:

          dcmp: a filecmp.dircmp ("directory comparison") instance.
          attr: a dircmp attribute name.

        """
        attr_val = self._get_dcmp_attr(dcmp, attr_name)
        if not attr_val:
            return
        # Otherwise, raise the test failure.

        attr_details = "\n".join(["dircmp.%s = %s" % (attr, self._get_dcmp_attr(dcmp, attr)) for
                                  attr in DIRCMP_ATTRS])
        details = ("Attribute %s non-empty for directory compare:\n%s" %
                   (repr(attr_name), indent(attr_details, "  ")))

        self.fail(format_msg(details))

    def _assert_files_equal(self, file_name, file_names, actual_dir, expected_dir,
                            format_msg, fuzzy=False):
        format_string = dedent("""\
        Potentially differing files: %s
        Displaying first genuine file difference: %s

        %%s""" % (repr(file_names), file_name))

        def assert_files_format_msg(assert_file_details):
            details = format_string % indent(assert_file_details, "  ")
            return format_msg(details)

        actual_path, expected_path = [os.path.join(dir_path, file_name) for dir_path in [actual_dir, expected_dir]]

        self.assertFilesEqual(actual_path, expected_path, fuzzy=fuzzy,
                              format_msg=assert_files_format_msg,
                              file_encoding=TEST_FILE_ENCODING, errors=DECODE_ERRORS)

    def _assert_common_files_equal(self, dcmp, format_msg, fuzzy=False):
        """
        Assert that the common files in dcmp are the same.

        Arguments:

          dcmp: a filecmp.dircmp ("directory comparison") instance.

        """
        file_names = self._get_dcmp_attr(dcmp, 'diff_files')
        if not file_names:
            return
        # Otherwise, at least one file has different contents.  Pass the files
        # along to self.assertFilesEqual() to take advantage of AssertFileMixin's
        # error reporting and, if fuzzy=True, to apply the more relaxed
        # fuzzy match comparison.
        expected_dir, actual_dir = self._get_dirs(dcmp)

        index_to_examine = 0
        while file_names:
            file_name = file_names[index_to_examine]
            self._assert_files_equal(file_name, file_names, actual_dir, expected_dir,
                                     format_msg=format_msg, fuzzy=fuzzy)
            file_names.pop(index_to_examine)
        # If got here, then all files were in fact the same.

    def assertDirectoriesEqual(self, actual_dir, expected_dir, format_msg=None,
                               fuzzy=False, file_encoding='utf-8', errors='strict'):
        """
        Assert that the contents of two directories are equal.

        Raises an exception if the two directories are not equal.

        Arguments:

          format_msg: a function that accepts a details string and returns
            the desired text for the assertion error message.

        """
        if format_msg is None:
            format_msg = lambda msg: msg

        self.assertFileExists(actual_dir, label='actual directory', format_msg=format_msg)
        self.assertFileExists(expected_dir, label='expected directory', format_msg=format_msg)

        # TODO: use dircmp's ignore and/or hide keyword arguments.
        dcmp = dircmp(expected_dir, actual_dir)

        subdir_format_msg = self._make_subdir_format_msg(actual_dir, expected_dir, format_msg=format_msg)

        self._assert_common_files_equal(dcmp, format_msg=subdir_format_msg, fuzzy=fuzzy)

        for attr in DIRCMP_ATTRS:
            self._assert_empty(dcmp, attr, format_msg=subdir_format_msg)

        for subdir in dcmp.common_dirs:
            expected_subdir = os.path.join(expected_dir, subdir)
            actual_subdir = os.path.join(actual_dir, subdir)
            self.assertDirectoriesEqual(actual_subdir, expected_subdir,
                                        format_msg=format_msg, fuzzy=True)
