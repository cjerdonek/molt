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

# TODO: rename this module to something like diffing.

"""
Provides support for recursive directory comparisons.

"""

from __future__ import absolute_import

import filecmp
import os
import sys

# TODO: remove the dependency on molt.defaults.
import molt.defaults as molt_defaults
import molt.general.io as molt_io


_ENCODING = molt_defaults.FILE_ENCODING


def compare_files(path1, path2):
    """
    Return whether the file contents at the given paths are the same.

    """
    return filecmp.cmp(path1, path2, shallow=False)


# TODO: replace uses of this class with FileComparer2.
class FileComparer(object):

    # TODO: this class should instead accept a function that returns None
    # if the strings are equal, otherwise a DiffInfo instance that
    # describes the difference.
    def __init__(self, match=None):
        """
        Parameters:

          match: a function that accepts two unicode strings, and returns
            whether they should be considered equal.  Defaults to the
            usual string equality operator.

        """
        if match is None:
            match = unicode.__eq__

        self.match_func = match

    def compare(self, path1, path2):
        _read = lambda path: molt_io.read(path, encoding=_ENCODING, errors=_ENCODING)

        self.left, self.right = map(_read, (path1, path2))

        return self.match_func(self.left, self.right)


class DirDiffInfo(tuple):

    """The return value of a call to DirComparer.diff().

    The paths returned by the properties of this class are relative to the
    directories that were compared.

    """

    def __new__(cls, dirs):
        tup = tuple([] for i in range(4))
        return super(DirDiffInfo, cls).__new__(cls, tup)

    def __init__(self, dirs):
        self.dirs = dirs

    def does_match(self):
        for seq in self:
            if len(seq) > 0:
                # Then there was a difference.
                return False
        return True

    @property
    def attr_names(self):
        return ["left_only", "right_only", "common_funny", "diff_files"]

    @property
    def left_only(self):
        return self[0]

    @property
    def right_only(self):
        return self[1]

    @property
    def common_funny(self):
        """
        Paths that are files in one directory and directories in the other.

        """
        return self[2]

    @property
    def diff_files(self):
        return self[3]


class Customizer(object):

    """Customizes DirComparer behavior."""

    def files_same(self, path1, path2):
        return compare_files(path1, path2)

    def on_diff_file(self, rel_path, result):
        """
        Parameters:

          rel_path: the path of the differing files relative to the
            top-level directories of the directories being compared.

          result: the return value of compare_files.

        """
        pass


# TODO: change this in the same way that FileComparer2 differs from FileComparer.
class DirComparer(object):

    # TODO: add a "max differences" argument that causes the function
    #   to terminate when that many differences are encountered.
    # TODO: add support for ignoring files matching a certain pattern, etc.
    # TODO: remove the compare parameter.
    def __init__(self, compare=None, ignore=None, custom=None):
        """
        Parameters:

          compare: [deprecated] a function that accepts two paths and
            returns whether the files at those paths should be considered
            the same.  Defaults to compare_files.  If provided, the
            custom argument is ignored.

          custom: an instance of a subclass of Customizer.

        """
        if compare is not None:
            custom = Customizer()
            custom.files_same = compare
        elif custom is None:
            custom = Customizer()

        compare_func = compare_files if compare is None else compare

        self.ignore = ignore
        self.compare_func = compare_func
        self.custom = custom

    def _diff(self, dcmp, results, leading_path=''):
        """
        Recursively compare a filecmp.dircmp instance.

        This method modifies the results container in place.

        Parameters:

          dcmp: a filecmp.dircmp instance.

          results: a three-tuple of (left_only, right_only, diff_files).

          leading_path: the path at which the directory comparison
            is taking place.  The path is relative to the top-level
            directories passed to the initial call to diff().

        """
        # TODO: simplify the implementation of this method if possible.
        # For example, eliminate the use of on-the-fly lambdas.
        make_rel_path = lambda name: os.path.join(leading_path, name)

        # Since the file comparer being used may be more forgiving than the
        # exact-match default, we need to check the names in dcmp.diff_files
        # again to see if any are the same under the looser condition.
        #
        # Since dircmp only does "shallow" file comparisons (i.e. doesn't
        # look at file contents), we need to check the files in
        # dcmp.same_files again to see if they might in fact be different.
        # See also: http://bugs.python.org/issue15250
        diff_files = []
        # The common_files list includes: same_files, diff_files, funny_files.
        for name in dcmp.common_files:
            paths = (os.path.join(path, name) for path in (dcmp.left, dcmp.right))
            result = self.custom.files_same(*paths)
            if not result is True:
                rel_path = make_rel_path(name)
                self.custom.on_diff_file(rel_path, result)
                diff_files.append(name)

        # Process the higher-level paths before recursing so notifications
        # about these paths will occur earlier.
        name_lists = (dcmp.left_only, dcmp.right_only, dcmp.common_funny, diff_files)
        for result_paths, names in zip(results, name_lists):
            new_paths = [make_rel_path(name) for name in names]
            result_paths.extend(new_paths)

        for dir_name, sub_dcmp in dcmp.subdirs.iteritems():
            path = make_rel_path(dir_name)
            self._diff(sub_dcmp, results, leading_path=path)


    # TODO: reimplement this method without using filecmp.dircmp because
    # this might be more straightforward and easier to understand given
    # filecmp.dircmp's use of shallow comparisons, etc.
    def diff(self, dir1, dir2):
        """
        Compare the directories at the given paths.

        This method raises an OSError if either directory does not exist.

        Returns a DirDiffInfo instance.

        """
        info = DirDiffInfo((dir1, dir2))
        dcmp = filecmp.dircmp(dir1, dir2, ignore=self.ignore)
        self._diff(dcmp, info)
        # Normalize the result sequences for testing and display purposes.
        map(lambda seq: seq.sort(), info)
        return info
