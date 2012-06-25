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
Provides functionality to locate files and folders in the project directory.

"""

from __future__ import absolute_import

import os

import molt
import molt.test


SETUP_PACKAGE_NAME = 'molt_setup'

# The below are relative to the source directory
GROOME_TEST_DIR = 'sub/groome/tests'
README_PATH = 'README.md'


class Locator(object):

    """
    Provides access to key files and folders in the project folder hierarchy.

    """

    def __init__(self, source_dir):
        """
        Arguments:

          source_dir: the path to a source distribution or source checkout,
            or None if one is not available (e.g. if running from a package
            install).

        """
        self.source_dir = source_dir

    def groome_tests_dir(self):
        if self.source_dir is None:
            return None
        return os.path.join(self.source_dir, GROOME_TEST_DIR)

    def doctest_paths(self):
        paths = []

        if self.source_dir is not None:
            readme_path = os.path.join(self.source_dir, README_PATH)
            paths.append(readme_path)

        return paths

    def extra_package_dirs(self):
        extra_package_dirs = []

        if self.source_dir is not None:
            setup_dir = os.path.join(self.source_dir, SETUP_PACKAGE_NAME)
            extra_package_dirs.append(setup_dir)

        return extra_package_dirs
