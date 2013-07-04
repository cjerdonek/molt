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
Provides support for accessing and operating on template directories.

"""

from __future__ import absolute_import

import logging
import os
from shutil import copytree
import stat

from molt.general.error import Error
from molt import defaults


def get_default_config_files():
    paths = ["%s%s" % (defaults.CONFIG_FILE_NAME, ext) for ext in defaults.CONFIG_FILE_EXTENSIONS]
    return paths


def _try_make_dir(dir_path):
    """
    Create a directory recursively and return whether successful.

    Raises an exception if not successful and nothing exists at the
    given path.

    """
    try:
        os.makedirs(dir_path)  # this creates recursively.
    except OSError:
        # Then most likely the leaf directory exists.
        if not os.path.exists(dir_path):
            # Then there was an unanticipated failure reason.
            raise
        return False
    return True


# TODO: eliminate this function.
def make_expected_dir(template_dir):
    chooser = DirectoryChooser()
    return chooser.get_expected_dir(template_dir)


# TODO: share code with DirectoryChooser.get_project_dir().
def make_project_dir(template_dir):
    return os.path.join(template_dir, defaults.TEMPLATE_PROJECT_DIR_NAME)


def make_available_dir(output_dir, format_dir_name=None):
    """
    Make a new directory -- creating a new directory name if necessary.

    Arguments:

      output_dir: the initial directory path to try.

      new_dir_name: a function that accepts a (dir_path, index) and
        returns a new directory name.  Defaults to the package default.

    """
    if format_dir_name is None:
        format_dir_name = defaults.FORMAT_NEW_DIR

    initial_dir = output_dir
    index = 1
    while True:
        if _try_make_dir(output_dir):
            return output_dir
        output_dir = format_dir_name(initial_dir, index)
        index += 1


def set_executable_bit(path):
    """
    Set the executable bits on a file.

    """
    exec_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    mode = os.stat(path)[stat.ST_MODE]
    mode = mode | exec_bits
    os.chmod(path, mode)


def stage_template_dir(source_dir, target_dir):
    """
    Copy the template directory, and set executable bits as necessary.

    Raises an Exception if target_dir already exists.

    """
    # copytree errors out if the target directory already exists.
    copytree(source_dir, target_dir)

    template_dir = TemplateDirectory(target_dir)
    lambda_paths = template_dir.get_lambda_paths()

    for path in lambda_paths:
        set_executable_bit(path)


class TemplateDirectory(object):

    """
    Represents a Groome template directory.

    """

    def __init__(self, path):
        self.path = path

        # TODO: remove this attribute.
        self._chooser = DirectoryChooser()

    def get_lambdas_dir(self):
        """
        Return the path to the lambdas directory, or None if not existing.

        """
        return self._chooser.get_lambdas_dir(self.path)

    def get_lambda_paths(self):
        """
        Return the paths to the lambdas in the lambdas directory.

        Returns all paths that are files and not hidden.

        """
        paths = []

        dir_path = self.get_lambdas_dir()
        if dir_path is None:
            return paths

        for base_path in os.listdir(dir_path):
            if base_path.startswith(os.curdir):
                # Skip hidden files.
                continue
            path = os.path.join(dir_path, base_path)
            if not os.path.isfile(path):
                # Skip directories.
                continue
            paths.append(path)

        return paths


# TODO: move the code in this class into the TemplateDirectory class.
class DirectoryChooser(object):

    """
    A class responsible for choosing directories based on command options.

    """

    # TODO: eliminate this method?
    def _make_path(self, template_dir, base_path):
        return os.path.join(template_dir, base_path)

    def _get_dir(self, template_dir, dir_name, is_required=False, display_name=None):
        """
        Arguments:

          display_name: the display name, suitable for beginning a sentence.

        """
        path = self._make_path(template_dir, dir_name)

        if os.path.exists(path):
            return path
        if not is_required:
            return None
        raise Error("%s not found at: %s" % (display_name, path))

    def get_project_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.TEMPLATE_PROJECT_DIR_NAME,
                             is_required=True,
                             display_name="Template structure directory")

    def get_partials_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.TEMPLATE_PARTIALS_DIR_NAME)

    def get_lambdas_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.TEMPLATE_LAMBDAS_DIR_NAME)

    def get_expected_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.TEMPLATE_EXPECTED_DIR_NAME)

    def get_config_path(self, path, template_dir):
        """
        Arguments:

          path: the user-provided path.  If None, looks for the configuration
            file in a default location in the given template directory.

        """
        if path is not None:
            return path
        # Otherwise, choose a default.

        default_config_files = get_default_config_files()
        paths = [self._make_path(template_dir, file_name) for file_name in default_config_files]

        for path in paths:
            if os.path.exists(path):
                return path
        # Otherwise, not found.

        prefix = "    "
        path_strings = prefix + ("\n" + prefix).join(default_config_files)
        raise Error("""Config file not found at any of the default locations
  in template directory: %s
%s""" % (template_dir, path_strings))
