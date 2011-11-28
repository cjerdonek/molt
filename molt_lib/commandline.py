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

import codecs
import logging
import os

from .common.optionparser import OptionParser
from .common.optionparser import UsageError


_log = logging.getLogger(__name__)


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


class DefaultOptions(object):
    """
    The default values that the OptionParser should use.

    """
    def __init__(self):
        self.config_path = ""
        self.destination_directory = ""
        self.source_root_directory = ""


def create_parser(defaults, suppress_help_exit, usage=USAGE):
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
    parser.add_option("-t", "--target", metavar='DIRECTORY', dest="target_directory",
                      action="store", type='string', default=defaults.destination_directory,
                      help='the directory in which to create the new project. '
                           'Defaults to the current working directory.')
    parser.add_option("-o", "--overwrite", dest="should_overwrite",
                      action="store_true", default=False,
                      help='whether to overwrite files in the target directory '
                           'if the target directory already exists.  Otherwise, '
                           'a new target directory is created by incrementing the '
                           'target directory name, for example "target_name (2)".')
    parser.add_option("-p", "--project-template", metavar='DIRECTORY', dest="project_directory",
                      action="store", type='string', default=defaults.source_root_directory,
                      help='the directory containing the project template.  '
                           'Defaults to the default template directory.')
    parser.add_option("-v", "--verbose", dest="is_verbose_logging_enabled",
                      action="store_true", default=False,
                      help="log verbosely.")
    parser.add_option("-g", "--generate-expected", dest="should_generate_expected",
                      action="store_true", default=False,
                      help='whether to regenerate the "expected" version of each '
                           'project template.  Regenerating versions does not '
                           'delete files but only overwrites them.  This option '
                           'is exposed mainly for molt development purposes.')
    parser.add_option("-h", "--help", action=help_action,
                      help="show this help message and exit.")

    return parser


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


def read_args(sys_argv, usage, defaults, current_working_directory):
    """
    Raises UsageError on bad arguments.


    """
    options, args = parse_args(sys_argv, suppress_help_exit=False, usage=usage, defaults=defaults)

    _log.debug("Configuration file: %s" % options.config_path)
    _log.debug("Project directory: %s" % options.project_directory)
    _log.debug("Target directory: %s" % options.target_directory)

    return options

