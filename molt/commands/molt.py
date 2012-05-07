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
Supplies the main method for the molt project.

"""

from __future__ import absolute_import

import codecs
from datetime import datetime
import logging
import os
import sys

import molt
from molt import io
from molt import commandline
from molt import config
from molt.common.error import Error
from molt.common.optionparser import UsageError
from molt.common.logging import configure_logging
from molt.project_type import ProjectType
from molt.render import Renderer
from molt.view import File

_log = logging.getLogger("main")


ENCODING_DEFAULT = 'utf-8'

ENCODING_CONFIG   = ENCODING_DEFAULT
ENCODING_OUTPUT   = ENCODING_DEFAULT
ENCODING_TEMPLATE = ENCODING_DEFAULT


def get_project_directory():
    lib_directory = os.path.dirname(molt.__file__)
    lib_directory = os.path.relpath(lib_directory)

    project_directory = os.path.normpath(os.path.join(lib_directory, os.pardir))

    return project_directory


def get_default_project_type():
    """
    Return the default project type as a ProjectType instance.

    """
    project_directory = get_project_directory()
    project_type_dir = os.path.join(project_directory, "project_types", "default")
    return ProjectType(project_type_dir)


def create_defaults(current_working_directory):

    project_type = get_default_project_type()

    defaults = commandline.DefaultOptions()

    defaults.config_path = project_type.get_config_path()
    defaults.destination_directory = current_working_directory
    defaults.source_root_directory = project_type.get_project_directory()

    return defaults


def read_file(path, encoding):
    """
    Return the contents of a file as a unicode string.

    """
    with codecs.open(path, "r", encoding=encoding) as f:
        text = f.read()

    return text


def make_output_directory_name(script_name, index):
    return "%s (%d)" % (script_name, index)


def render_project(project_directory, output_directory, config_path, extra_template_dirs):

    render_config = config.read_render_config(config_path, encoding=ENCODING_CONFIG)
    context = render_config.context

    renderer = Renderer(root_source_dir=project_directory, target_dir=output_directory,
                        context=context, extra_template_dirs=extra_template_dirs,
                        output_encoding=ENCODING_OUTPUT)

    renderer.render()


def generate_expected():
    project_type = get_default_project_type()

    _log.info("Generating expected for project type: %s" % project_type.label)

    project_directory = project_type.get_project_directory()
    config_path = project_type.get_config_path()
    output_directory = project_type.get_expected_directory()
    extra_template_dirs = project_type.get_template_directories()

    render_project(project_directory, output_directory, config_path, extra_template_dirs)


def do_program_body(sys_argv, usage):

    current_working_directory = os.curdir
    defaults = create_defaults(current_working_directory)
    options = commandline.read_args(sys_argv, usage=usage, defaults=defaults)

    # TODO: do something nicer than this if-else block.
    if options.should_generate_expected:
        generate_expected()
    else:
        project_directory = options.project_directory
        config_path = options.config_path
        target_directory = options.target_directory

        # TODO: need to address extra_template_dirs for command-line-provided project templates.
        project_type = get_default_project_type()
        extra_template_dirs = project_type.get_template_directories()

        render_config = config.read_render_config(config_path, encoding=ENCODING_CONFIG)
        script_name = render_config.project_label

        # TODO: fix this hack.
        index = 1
        output_directory_name = script_name
        while True:
            output_directory = os.path.join(target_directory, output_directory_name)
            if options.should_overwrite or not os.path.exists(output_directory):
                break
            output_directory_name = make_output_directory_name(script_name, index)
            index += 1

        if not io.create_directory(output_directory):
            _log.info("Overwriting output directory: %s" % output_directory)
        _log.debug("Output directory: %s" % output_directory)

        render_project(project_directory, output_directory, config_path, extra_template_dirs)

        _log.info("Printing output directory to stdout...")
        print output_directory

    _log.info("Done.")


def main(sys_argv, configure_logging=configure_logging, process_args=do_program_body):
    """
    Execute this script's main function, and return the exit status.

    Args:

      process_args: the function called within this method's try-except
        block and that accepts sys.argv as a single parameter.
        This parameter is exposed only for unit testing purposes.  It
        allows the function's exception handling logic to be tested
        more easily.

    """
    # TODO: follow all of the recommendations here:
    # http://www.artima.com/weblogs/viewpost.jsp?thread=4829

    # Configure logging before parsing options for real.
    logging_level = logging.DEBUG if commandline.is_verbose_logging_enabled(sys_argv) else logging.INFO
    configure_logging(logging_level)

    try:
        process_args(sys_argv, commandline.USAGE)
        return 0
    # TODO: include KeyboardInterrupt in the template version of this file.
    except UsageError as err:
        s = """\
Command-line usage error: %s

Pass -h or --help for help documentation and available options.""" % err
        _log.error(s)

        return 2
    except Error, err:
        _log.error(err)
        return 1


if __name__ == "__main__":
    result = main(sys.argv)
    sys.exit(result)
