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
Exposes a Molter class to render a template directory.

"""

from __future__ import absolute_import

import logging
import os
from shutil import copyfile
from subprocess import Popen, PIPE, STDOUT

from pystache import Renderer as PystacheRenderer

import molt
from molt.general import io
from molt.general.error import Error
from molt.general.popen import call_script
from  molt import defaults
from molt.dirutil import DirectoryChooser


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


def _lambda_from_script(path):
    def func(u=None):
        if u is None:
            u = ''
        bytes_in = u.encode(defaults.LAMBDA_ENCODING, errors=defaults.ENCODING_ERRORS)

        stdout, stderr, return_code = call_script(path, bytes_in)

        return stdout.decode(defaults.LAMBDA_ENCODING, errors=defaults.ENCODING_ERRORS)

    return func


class Molter(object):

    def __init__(self, encoding='utf-8', decode_errors='strict', chooser=None):
        if chooser is None:
            chooser = DirectoryChooser()

        self.chooser = chooser
        self.decode_errors = decode_errors
        self.encoding = encoding

    def _get_config_path(self, template_dir, config_path):
        return self.chooser.get_config_path(config_path, template_dir)

    def read_config(self, template_dir, config_path=None):
        path = self._get_config_path(template_dir, config_path)
        try:
            return io.deserialize(path, self.encoding, self.decode_errors)
        except Exception, err:
            # TODO: reraise existing exception and add additional info instead
            #   of swallowing caught exception and raising a new one.
            raise Error("Error loading config at: %s\n-->%s" % (path, err))

    def get_context(self, template_dir, config_path=None):
        """"
        Return the context (including lambdas) for the given template.

        """
        data = self.read_config(template_dir, config_path)

        context = data[defaults.CONFIG_CONTEXT_KEY]

        lambdas_dir = self.chooser.get_lambdas_dir(template_dir)
        lambdas = [] if lambdas_dir is None else self.get_lambdas(lambdas_dir)

        # TODO: raise an exception if lambdas and context intersect?
        context.update(lambdas)

        return context

    def get_lambdas(self, lambda_dir):
        lambdas = {}
        for file_name in os.listdir(lambda_dir):
            if file_name.startswith('.'):
                # For example, skip .DS_Store.
                continue

            script_path = os.path.join(lambda_dir, file_name)
            func = _lambda_from_script(script_path)
            root_name, ext = os.path.splitext(file_name)

            root_name = unicode(root_name)

            lambdas[root_name] = func

        return lambdas

    # TODO: create a class to hold and pass the arguments along.
    def molt(self, template_dir, output_dir, config_path=None):
        chooser = self.chooser

        project_dir = chooser.get_project_dir(template_dir)
        partials_dir = chooser.get_partials_dir(template_dir)
        lambdas_dir = chooser.get_lambdas_dir(template_dir)
        config_path = self._get_config_path(template_dir, config_path)

        context = self.get_context(template_dir, config_path)

        _log.info("""\
Rendering:

  Structure directory:   %s
  Partial directory:   %s
  Lambdas directory:   %s
  Config file:         %s

  Destination: %s
    """ % (project_dir, partials_dir, lambdas_dir, config_path, output_dir))

        search_dirs = [partials_dir]

        pystache_renderer = PystacheRenderer(search_dirs=search_dirs, file_encoding=self.encoding)

        renderer = _Renderer(pystache_renderer)

        renderer.render(structure_dir=project_dir, context=context, output_dir=output_dir)
        _log.info("Wrote new project to: %s" % repr(output_dir))


# TODO: combine this class with the Molter class.
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
        io.write(u, target_path, defaults.OUTPUT_FILE_ENCODING, defaults.ENCODING_ERRORS)

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

    def render(self, structure_dir, context, output_dir):
        """
        Recursively render the contents of a directory to an output directory.

        Arguments:

          output_dir: a path to an existing directory.

        """
        # Validate arguments because this is the entry point to a method
        # called by end-users.
        # TODO: move this argument validation to the beginning of the function
        #   actually called by end-users.
        if not os.path.exists(structure_dir):
            raise (Error("Structure directory missing: %s" % structure_dir))
        if not os.path.exists(output_dir):
            raise (Error("Output directory missing: %s" % output_dir))

        self._molt_dir(structure_dir, context, output_dir)
