# encoding: utf-8
#
# Copyright (C) 2011 Chris Jerdonek. All rights reserved.
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
Exposes a Renderer class to render project files from template files.

"""

from __future__ import absolute_import

import logging
import os

from . import io
from .view import File


_log = logging.getLogger(__name__)


class Renderer(object):

    def __init__(self, root_source_dir, target_dir, context, extra_template_dirs, output_encoding):
        self.context = context
        self.encoding = output_encoding
        self.extra_template_dirs = extra_template_dirs
        self.root_source_dir = root_source_dir
        self.target_dir = target_dir

    def render(self):
        root_dir = self.root_source_dir

        if not os.path.exists(root_dir):
            raise Exception("Source directory does not exist: %s" % root_dir)

        _log.debug("Rendering to: %s" % self.target_dir)
        for (dir_path, dir_names, file_names) in os.walk(self.root_source_dir):
            # TODO: eliminate the cut-and-paste between the dir_name and file_name for loops.
            for dir_name in dir_names:
                source_dir = os.path.join(dir_path, dir_name)
                # TODO: os.path.relpath() is available only as of Python 2.6.
                # Make this work in Python 2.5.
                rel_path = os.path.relpath(source_dir, self.root_source_dir)
                target_dir = os.path.join(self.target_dir, rel_path)

                io.create_directory(target_dir)

            for file_name in file_names:
                source_path = os.path.join(dir_path, file_name)
                rel_path = os.path.relpath(source_path, self.root_source_dir)
                self.render_rel_path(rel_path)

    def render_rel_path(self, rel_path):
        """
        rel_path is a path relative to the source directory.

        """
        # By bare path, we mean the path without the template extension, for
        # example "README.md" for "README.md.mustache".
        bare_rel_path, ext = os.path.splitext(rel_path)

        source_path = os.path.join(self.root_source_dir, rel_path)
        target_path = os.path.join(self.target_dir, bare_rel_path)

        self.render_path(source_path, target_path)

    def render_path(self, source_path, target_path):
        source_dir, source_file_name = os.path.split(source_path)

        # Pystache allows us to pass only the template name and not the
        # template path.  Strip the template file extension to get the name.
        template_name, ext = os.path.splitext(source_file_name)

        source_dir = os.path.dirname(source_path)

        template_dirs = [source_dir] + self.extra_template_dirs

        view = File(context=self.context)
        view.template_name = template_name
        view.template_path = template_dirs

        rendered = view.render()

        io.write_file(rendered, target_path, encoding=self.encoding)

