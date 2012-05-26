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
Exposes functionality to choose directories to use based on user input.

"""

from __future__ import absolute_import

import os

from molt.common.error import Error
from molt import defaults


def get_default_config_files():
    paths = ["%s%s" % (defaults.CONFIG_FILE_NAME, ext) for ext in defaults.CONFIG_FILE_EXTENSIONS]
    return paths


def _try_make_dir(dir_path):
    """
    Make the given directory and return whether successful.

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


def make_output_dir(output_dir, default_output_dir):
    if output_dir is None:
        output_dir = default_output_dir

    initial_output_dir = output_dir
    index = 1
    while True:
        if _try_make_dir(output_dir):
            return output_dir
        output_dir = defaults.OUTPUT_DIR_FORMAT % (initial_output_dir, index)
        index += 1



class DirectoryChooser(object):

    """
    A class responsible for choosing directories based on command options.

    """

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
        raise Error("%s not found in default location\n"
                    "  in template directory: %s" % (display_name, path))

    def get_project_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.PROJECT_DIR_NAME,
                             is_required=True, display_name="Project directory")

    def get_partials_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.PARTIALS_DIR_NAME)

    def get_lambdas_dir(self, template_dir):
        return self._get_dir(template_dir, defaults.LAMBDAS_DIR_NAME)

    def get_config_path_string(self):
        s = ("looking in the template directory for one of: %s." %
             ", ".join(get_default_config_files()))

        return s

    def get_config_path(self, path, template_dir):
        """
        Arguments:

          path: the user-provided path.

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

        indent = "    "
        path_strings = indent + ("\n" + indent).join(default_config_files)
        raise Error("""Config file not found at any of the default locations
  in template directory: %s
%s""" % (template_dir, path_strings))