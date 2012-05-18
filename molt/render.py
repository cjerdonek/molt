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
Exposes a Renderer class to render a project template.

"""

from __future__ import absolute_import

import logging
import os
from shutil import copyfile

from pystache import Renderer as PystacheRenderer

import molt
from molt.common import io
from molt.common.error import Error
from molt.view import File


OUTPUT_ENCODING = 'utf-8'
ENCODE_ERRORS = 'strict'

TEMPLATE_EXT = '.mustache'
SKIP_EXT = '.skip'


_log = logging.getLogger(__name__)


def preprocess_filename(filename):
    is_template = False

    root, ext = os.path.splitext(filename)

    if ext == TEMPLATE_EXT:
        subroot, ext = os.path.splitext(root)
        if ext == SKIP_EXT:
            # For example, "template.skip.mustache".
            filename = subroot + TEMPLATE_EXT
        else:
            # For example, "README.md.mustache".
            filename = root
            is_template = True

    return filename, is_template


class Molter(object):

    def __init__(self, encoding='utf-8', decode_errors='strict'):
        self.encoding = encoding
        self.decode_errors = decode_errors

    def read_config(self, path):
        try:
            return io.deserialize(path, self.encoding, self.decode_errors)
        except Exception, err:
            # TODO: reraise or add to existing exception
            raise Error("Error loading config at: %s\n-->%s" % (path, err))

    def get_context(self, config_data):
        return config_data['context']

    def molt(self, project_dir, partials_dir, config_path, output_dir):
        _log.info("""\
    Rendering--

      project:  %s
      partials: %s
      config:   %s

      To:       %s
    """ % (project_dir, partials_dir, config_path, output_dir))

        search_dirs = [partials_dir]

        pystache_renderer = PystacheRenderer(search_dirs=search_dirs, file_encoding=self.encoding)

        renderer = _Renderer(pystache_renderer)

        config_data = self.read_config(config_path)
        context = self.get_context(config_data)

        renderer.render(project_dir=project_dir, context=context, output_dir=output_dir)


class _Renderer(object):

    """
    Exposes a render() method responsible for raw rendering of a directory.

    """

    def __init__(self, pystache_renderer):
        """
        Arguments:

          pystacher: a pystache.Renderer instance.

        """
        self.pystacher = pystache_renderer

    def _parse_basename(self, path, context, preprocess):
        """
        Arguments:

          preprocess: a function that accepts a basename and returns a
            (basename, is_template) pair.

        """
        dir_path, basename = os.path.split(path)

        basename2, is_template = preprocess(basename)
        basename3 = self.pystacher.render(basename2, context)

        if not basename3:
            raise Exception("Basename cannot be empty: %s > %s > %s\n"
                            "  in path: %s" %
                            (repr(basename), repr(basename2), repr(basename3), dir_path))
        return basename3, is_template


    def parse_filename(self, path, context):
        """
        Return the pair (filename, is_template).

        """
        return self._parse_basename(path, context, preprocess_filename)


    def parse_dirname(self, path, context):
        """
        Return the pair (filename, is_template).

        """
        return self._parse_basename(path, context, lambda name: (name, False))

    def _render_path_to_string(self, path, context):
        """
        Render the template at a path to a unicode string.

        """
        return self.pystacher.render_path(path, context)

    def _render_path_to_file(self, path, context, target_path):
        """
        Render the template at a path to a file.

        """
        u = self._render_path_to_string(path, context)
        io.write(u, target_path, OUTPUT_ENCODING, ENCODE_ERRORS)

    def molt_file(self, path, context, output_dir):
        filename, is_template = self.parse_filename(path, context)

        new_path = os.path.join(output_dir, filename)

        if not is_template:
            copyfile(path, new_path)
        else:
            self._render_path_to_file(path, context, new_path)

    def _molt_dir(self, dir_path, context, output_dir):
        """
        Recursively render the contents of a directory to an output directory.

        Arguments:

          output_dir: a path to an existing directory.

        """
        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if not os.path.isdir(path):
                self.molt_file(path, context, output_dir)
                continue
            # Otherwise, it is a directory.
            new_name = self.parse_dirname(path, context)[0]
            new_output_dir = os.path.join(output_dir, new_name)
            os.mkdir(new_output_dir)
            self._molt_dir(path, context, new_output_dir)

    def render(self, project_dir, context, output_dir):
        """
        Recursively render the contents of a directory to an output directory.

        Arguments:

          output_dir: a path to an existing directory.

        """
        try:
            self._molt_dir(project_dir, context, output_dir)
        except OSError:
            if not os.path.exists(project_dir):
                raise (Error("Project directory missing: %s" % project_dir))
            raise
