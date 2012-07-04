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

from functools import wraps
import os

import molt
import molt.test


# The below are relative to the source root (aka the project directory).
_GROOME_TEST_DIR = 'sub/groome/tests'
_README_PATH = 'README.md'
_SETUP_PACKAGE_DIR = 'molt_setup'

# The below are relative to the main Molt package directory.
_DEMO_TEMPLATE_DIR = 'demo'
_TEST_DATA_DIR = 'test/data'


def package_dir(get_relpath):
    """
    Return a new method that returns the path to a package sub-path.

    Use this as a method decorator.

    """
    @wraps(get_relpath)
    def make_path(self):
        return os.path.join(self.package_dir, get_relpath(self))

    return make_path


def source_dir(get_relpath):
    """
    Return a new method that returns the path to a source sub-path.

    Use this as a method decorator.

    """
    @wraps(get_relpath)
    def make_path(self):
        if self.source_dir is None:
            return None
        return os.path.join(self.source_dir, get_relpath(self))

    return make_path


def source_dirs(get_relpaths):
    """
    Return a new method that returns the paths to a list of source sub-paths.

    Use this as a method decorator.

    """
    @wraps(get_relpaths)
    def make_paths(self):
        if self.source_dir is None:
            return []
        return [os.path.join(self.source_dir, rel_path) for rel_path in get_relpaths(self)]

    return make_paths


class Locator(object):

    """
    Provides access to key files and folders in the project folder hierarchy.

    """

    def __init__(self, package_dir=None, source_dir=None):
        """
        Arguments:

          package_dir: the path to the Molt package directory.  Defaults
            to detecting the location via molt.__file__.

          source_dir: the path to a source distribution or source checkout,
            or None if one is not available (e.g. if running from a package
            install).

        """
        if package_dir is None:
            package_dir = os.path.dirname(molt.__file__)

        self.package_dir = package_dir
        self.source_dir = source_dir

    @property
    @source_dir
    def groome_tests_dir(self):
        return _GROOME_TEST_DIR

    @property
    @source_dirs
    def doctest_paths(self):
        return [_README_PATH]

    @property
    @source_dirs
    def extra_package_dirs(self):
        return [_SETUP_PACKAGE_DIR]

    @property
    @package_dir
    def demo_template_dir(self):
        return _DEMO_TEMPLATE_DIR

    @property
    @package_dir
    def test_data_dir(self):
        return _TEST_DATA_DIR
