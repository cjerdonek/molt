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

from .logging import configure_logging
from .optionparser import OptionParser
from .optionparser import UsageError
from .view import File

_log = logging.getLogger("main")


ENCODING_CONFIG   = 'utf-8'
ENCODING_OUTPUT   = 'utf-8'
ENCODING_TEMPLATE = 'utf-8'

# TODO: add a version option -V that reads the package version number.

# We escape the leading "%" so that the leading "%p" is not interpreted as
# a Python string formatting conversion specifier.  The optparse.OptionParser
# class, however, recognizes "%prog" by replacing it with the current
# script name when passed to the constructor as a usage string.
USAGE = """%prog [options]

Create a new Python project.

This script creates a new Python project from a project template using
values from a configuration file, and prints the destination directory
to standard output."""


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
        self.mustache_directory = ""


def get_project_directory():
    lib_directory = os.path.dirname(__file__)
    project_directory = os.path.normpath(os.path.join(lib_directory, os.pardir))

    return project_directory


# TODO: move the string literals to a more visible location.
def create_defaults(current_working_directory):
    project_directory = get_project_directory()
    template_directory = os.path.join("template", "default")

    defaults = DefaultOptions()

    defaults.config_path = os.path.join(template_directory, "config.yaml")
    defaults.destination_directory = current_working_directory
    defaults.mustache_directory = os.path.join(template_directory, "mustache")

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
    parser.add_option("-d", "--destination", metavar='DIRECTORY', dest="destination_directory",
                      action="store", type='string', default=defaults.destination_directory,
                      help='the directory in which to create the new project. '
                           'Defaults to the current working directory.')
    parser.add_option("-o", "--overwrite", dest="should_overwrite",
                      action="store_true", default=False,
                      help='whether to overwrite files in the destination directory '
                           'if the destination directory already exists.')
    parser.add_option("-t", "--template", metavar='DIRECTORY', dest="template_directory",
                      action="store", type='string', default=defaults.mustache_directory,
                      help='the directory containing the project template.  '
                           'Defaults to the default template directory.')
    parser.add_option("-v", "--verbose", dest="is_verbose_logging_enabled",
                      action="store_true", default=False,
                      help="log verbosely.")
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


def write_file(text, path, encoding):
    """
    Write a unicode string to a file.

    """
    with codecs.open(path, "w", encoding=encoding) as f:
        f.write(text)
    _log.debug("Wrote: %s" % path)


def render_template(template, values):

    rendered = pystache.render(template, values)

    return rendered


def make_project_directory_name(script_name, index):
    return "%s_%s" % (script_name, index)


def create_directory(path):
    """
    Create a directory if not there, and return whether one was created.

    """
    if not os.path.exists(path):
        os.mkdir(path)
        _log.debug("Created directory: %s" % path)
        return True
    if os.path.isdir(path):
        return False
    raise Error("Path already exists and is not a directory: %s" % path)


def do_program_body(sys_argv, usage):

    current_working_directory = os.curdir
    options = read_args(sys_argv, usage=usage, current_working_directory=current_working_directory)

    config_path = options.config_path
    destination_directory = options.destination_directory
    template_directory = options.template_directory

    template_path = os.path.join(template_directory, 'README.md.mustache')
    template = read_file(template_path, encoding=ENCODING_TEMPLATE)

    context = unserialize_yaml_file(config_path, encoding=ENCODING_CONFIG)

    view = File(template=template, context=context)
    script_name = context['script_name']

    index = 1
    project_directory_name = script_name
    while True:
        project_directory = os.path.join(destination_directory, project_directory_name)
        if options.should_overwrite or not os.path.exists(project_directory):
            break
        project_directory_name = make_project_directory_name(script_name, index)
        index += 1

    if not create_directory(project_directory):
        _log.info("Overwriting project: %s" % project_directory)
    _log.debug("Project directory: %s" % project_directory)

    destination_path = os.path.join(project_directory, 'README.md')

    rendered = view.render()

    write_file(rendered, destination_path, encoding=ENCODING_OUTPUT)
    _log.info("Printing destination directory to stdout...")
    print project_directory
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


