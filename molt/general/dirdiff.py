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
Provides functionality to diff directories recursively.

"""

from __future__ import absolute_import

from filecmp import cmpfiles, dircmp
import os
import sys


class Differ(object):

    # TODO: add a "max differences" argument that causes the function
    #   to terminate when that many differences are encountered.
    # TODO: add support for fuzzy matching and ignoring files matching
    #   a certain pattern, etc.
    # TODO: add a match_file argument that defaults to using cmpfiles.
    def __init__(self):
        pass

    def _diff(self, dcmp, results, leading_path=''):
        """
        Recursively compare a filecmp.dircmp instance.

        This method modifies the results container in place.

        Arguments:

          dcmp: a filecmp.dircmp instance.

          results: a three-tuple of (left_only, right_only, diff_files).

          leading_path: a path to prepend to each path added to the
            results container.

        """
        make_path = lambda name: os.path.join(leading_path, name)

        attrs = ['left_only', 'right_only', 'diff_files']
        for result_paths, attr in zip(results, attrs):
            paths = [make_path(name) for name in getattr(dcmp, attr)]
            result_paths.extend(paths)

        # Since dircmp only does "shallow" file comparisons (i.e. doesn't
        # look at file contents), we need to check the same files manually.
        # See also: http://bugs.python.org/issue15250
        (match, mismatch, errors) = cmpfiles(dcmp.left, dcmp.right, dcmp.same_files, shallow=False)
        new_diff_files = [make_path(name) for name in (mismatch + errors)]
        results[2].extend(new_diff_files)

        for dir_name, sub_dcmp in dcmp.subdirs.iteritems():
            path = make_path(dir_name)
            self._diff(sub_dcmp, results, leading_path=path)

    # TODO: add a diff_path function to customize file comparison.
    #   This lets us keep file-reading code out of this module.
    def diff(self, dir1, dir2):
        """
        Compare the directories at the given path.

        This method raises an OSError if either directory does not exist.

        """
        # The 3-tuple is (left_only, right_only, diff_files).
        results = tuple([] for i in range(3))

        dcmp = dircmp(dir1, dir2)

        self._diff(dcmp, results)

        # Normalize the results sequences for testing and display purposes.
        map(lambda seq: seq.sort(), results)

        return results
