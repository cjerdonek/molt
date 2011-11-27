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

import pystache
import yaml

from . import io
from .logging import configure_logging
from .optionparser import OptionParser
from .optionparser import UsageError
from .render import Renderer
from .view import File

_log = logging.getLogger("main")


ENCODING_DEFAULT = 'utf-8'

ENCODING_CONFIG   = ENCODING_DEFAULT
ENCODING_OUTPUT   = ENCODING_DEFAULT
ENCODING_TEMPLATE = ENCODING_DEFAULT

# TODO: add a version option -V that reads the package version number.

# We escape the leading "%" so that the leading "%p" is not interpreted as
# a Python string formatting conversion specifier.  The optparse.OptionParser
# class, however, recognizes "%prog" by replacing it with the current
# script name when passed to the constructor as a usage string.
USAGE = """%prog [options]

Create a new Python project.

This script creates a new Python project from a project template using
values from a configuration file.  It prints the output directory to
standard output when complete."""


class Error(Exception):
    """Base class for exceptions defined in this project."""
    pass


class DefaultOptions(object):
    """
    The default values that the OptionParser should use.

    """
    def __init__(self):
        self.config_path = ""
        self.destination_directory = ""
        self.source_root_directory = ""


def get_project_directory():
    lib_directory = os.path.dirname(__file__)
    project_directory = os.path.normpath(os.path.join(lib_directory, os.pardir))

    return project_directory


def get_license_directory():
    project_directory = get_project_directory()
    return os.path.join(project_directory, "template")


def get_partials_directory():
    project_directory = get_project_directory()
    return os.path.join(project_directory, "template", "default", "partials")


# TODO: move the string literals to a more visible location.
def create_defaults(current_working_directory):
    project_directory = get_project_directory()
    template_directory = os.path.join(project_directory, "template", "default")

    defaults = DefaultOptions()

    defaults.config_path = os.path.join(template_directory, "config.yaml")
    defaults.destination_directory = current_working_directory
    defaults.source_root_directory = os.path.join(template_directory, "project")

    return defaults


def create_parser(defaults, suppress_help_exit, usage=None):
    """
    Return an OptionParser for the program.

    """
    help_action = "store_true" if suppress_help_exit else "help"

    parser = OptionParser(usage=usage, add_help_option=False)

    # TODO: explicitly add a version option?
    parser.add_option("-c", "--config", metavar='FILE', dest="config_path",
                      action="store", type='string', default=defaults.config_path,
                      help='the path to the configuration file that contains, '
                           'for example, the values with which to populate the template.  '
                           'Defaults to the default configuration file.')
    parser.add_option("-t", "--target", metavar='DIRECTORY', dest="destination_directory",
                      action="store", type='string', default=defaults.destination_directory,
                      help='the directory in which to create the new project. '
                           'Defaults to the current working directory.')
    parser.add_option("-o", "--overwrite", dest="should_overwrite",
                      action="store_true", default=False,
                      help='whether to overwrite files in the target directory '
                           'if the target directory already exists.  Otherwise, '
                           'a new target directory is created by incrementing the '
                           'target directory name, for example "target_name (2)".')
    parser.add_option("-p", "--project-template", metavar='DIRECTORY', dest="template_directory",
                      action="store", type='string', default=defaults.source_root_directory,
                      help='the directory containing the project template.  '
                           'Defaults to the default template directory.')
    parser.add_option("-v", "--verbose", dest="is_verbose_logging_enabled",
                      action="store_true", default=False,
                      help="log verbosely.")
    parser.add_option("--generate-expected", dest="should_generate_expected",
                      action="store_true", default=False,
                      help='whether to regenerate the "expected" version of each '
                           'project template.  Regenerating versions does not '
                           'delete files but only overwrites them.  This option '
                           'is exposed mainly for molt development purposes.')
    parser.add_option("-h", "--help", action=help_action,
                      help="show this help message and exit.")

    return parser


def parse_args(sys_argv, suppress_help_exit, usage=None, defaults=None):
    """
    Parse arguments and return (options, args).

    Raises UsageError on command-line usage error.

    """
    if defaults is None:
        defaults = DefaultOptions()

    args = sys_argv[1:]

    parser = create_parser(defaults, suppress_help_exit=suppress_help_exit, usage=usage)
    options, args = parser.parse_args(args)

    return options, args


def is_verbose_logging_enabled(sys_argv):
    """
    Return whether verbose logging is enabled.

    """
    try:
        # Suppress the help option to prevent exiting.
        options, args = parse_args(sys_argv, suppress_help_exit=True)
    except UsageError:
        # Default to normal logging on error.
        return False

    return options.is_verbose_logging_enabled


def read_args(sys_argv, usage, current_working_directory):
    """
    Raises UsageError on bad arguments.


    """
    defaults = create_defaults(current_working_directory)
    options, args = parse_args(sys_argv, suppress_help_exit=False, usage=usage, defaults=defaults)

    _log.debug("Configuration file: %s" % options.config_path)
    _log.debug("Destination directory: %s" % options.destination_directory)
    _log.debug("Template directory: %s" % options.template_directory)

    return options



def unserialize_yaml_file(path, encoding):
    """
    Deserialize a yaml file.

    """
    with codecs.open(path, "r", encoding=encoding) as f:
        data = yaml.load(f)

    return data


def read_file(path, encoding):
    """
    Return the contents of a file as a unicode string.

    """
    with codecs.open(path, "r", encoding=encoding) as f:
        text = f.read()

    return text


def render_template(template, values):

    rendered = pystache.render(template, values)

    return rendered


def make_output_directory_name(script_name, index):
    return "%s_%s" % (script_name, index)


def read_template(path):
    template = read_file(path, encoding=ENCODING_TEMPLATE)
    return template


def render_file(file_path, target_directory, context, extra_template_dirs):
    view = File(context)


def do_program_body(sys_argv, usage):

    current_working_directory = os.curdir
    options = read_args(sys_argv, usage=usage, current_working_directory=current_working_directory)

    config_path = options.config_path
    destination_directory = options.destination_directory
    template_directory = options.template_directory
    should_generate_expected = options.should_generate_expected

    if should_generate_expected:
        # TODO: implement this.
        raise Error("Option not implemented.")

    license_directory = get_license_directory()
    partials_directory = get_partials_directory()

    context = unserialize_yaml_file(config_path, encoding=ENCODING_CONFIG)

    script_name = context['script_name']

    index = 1
    output_directory_name = script_name
    while True:
        output_directory = os.path.join(destination_directory, output_directory_name)
        if options.should_overwrite or not os.path.exists(output_directory):
            break
        output_directory_name = make_output_directory_name(script_name, index)
        index += 1

    if not io.create_directory(output_directory):
        _log.info("Overwriting output directory: %s" % output_directory)
    _log.debug("Output directory: %s" % output_directory)

    renderer = Renderer(root_source_dir=template_directory, target_dir=output_directory,
                        context=context, extra_template_dirs=[partials_directory],
                        output_encoding=ENCODING_OUTPUT)

    renderer.render()

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
    logging_level = logging.DEBUG if is_verbose_logging_enabled(sys_argv) else logging.INFO
    configure_logging(logging_level)

    try:
        process_args(sys_argv, USAGE)
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


