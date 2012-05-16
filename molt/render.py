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
Exposes a Renderer class to render a project template.

"""

from __future__ import absolute_import

import logging
import os
from shutil import copyfile

from pystache import Renderer as Pystacher

import molt
from molt.common import io
from molt.view import File


OUTPUT_ENCODING = 'utf-8'
ENCODE_ERRORS = 'strict'

TEMPLATE_EXT = '.mustache'
SKIP_EXT = '.skip'


_log = logging.getLogger(__name__)


def render():
    ENCODING = 'utf-8'
    DECODE_ERRORS = 'strict'

    source_dir = os.path.dirname(molt.__file__)
    project_dir = os.path.join(source_dir, os.pardir)
    example_dir = os.path.join(project_dir, 'examples', 'PythonScript')
    output_dir = 'output'

    template_dir = os.path.join(example_dir, 'template')
    config_path = os.path.join(example_dir, 'sample.json')

    data = io.deserialize(config_path, ENCODING, DECODE_ERRORS)
    data = data['mustache']

    pystacher = Pystacher()

    molter = Molter(pystacher)

    test_path = os.path.join(template_dir, "{{project}}.py.mustache")

    os.mkdir("output")
    molter.molt_dir(template_dir, data, "output")


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

    def __init__(self, pystacher):
        """
        Arguments:

          pystacher: a pystache.Renderer instance.

        """
        self.pystacher = pystacher

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

    def molt_dir(self, dir_path, context, output_dir):
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
            self.molt_dir(path, context, new_output_dir)


class Renderer(object):

    def __init__(self, root_source_dir, target_dir, context, extra_template_dirs, output_encoding):
        self.context = context
        self.encoding = output_encoding
        self.extra_template_dirs = extra_template_dirs
        self.root_source_dir = root_source_dir
        self.target_dir = target_dir

    def render(self):
        root_dir = self.root_source_dir
        target_dir = self.target_dir

        # TODO: Eliminate cut-and-paste with similar log message below.
        _log.info("""\
Rendering template directory...
  From: %s
  To:   %s""" % (root_dir, target_dir))

        if not os.path.exists(root_dir):
            raise Exception("Source directory does not exist: %s" % root_dir)

        for (dir_path, dir_names, file_names) in os.walk(self.root_source_dir):
            # TODO: skip special files and directories.
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

                # TODO: allow the template extension to be configurable.
                extension = os.path.splitext(rel_path)[1]
                if extension != ".mustache":
                    _log.info("Skipping non-template file: %s" % rel_path)
                    continue

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

        _log.debug("""\
Rendering template:
  From: %s
  To:   %s""" % (source_path, target_path))
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


if __name__ == "__main__":
    ENCODING = 'utf-8'
    DECODE_ERRORS = 'strict'

    source_dir = os.path.dirname(molt.__file__)
    project_dir = os.path.join(source_dir, os.pardir)
    example_dir = os.path.join(project_dir, 'examples', 'PythonScript')
    output_dir = 'output'

    template_dir = os.path.join(example_dir, 'template')
    config_path = os.path.join(example_dir, 'sample.json')

    data = io.deserialize(config_path, ENCODING, DECODE_ERRORS)
    data = data['mustache']

    pystacher = Pystacher()

    molter = Molter(pystacher)

    test_path = os.path.join(template_dir, "{{project}}.py.mustache")

    os.mkdir("output")
    molter.molt_dir(template_dir, data, "output")
