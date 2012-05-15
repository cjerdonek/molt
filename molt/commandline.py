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

# TODO: use argparse instead of optparse:
#   http://docs.python.org/library/argparse.html#module-argparse
from .common.optionparser import OptionParser
from .common.optionparser import UsageError


OPTION_RUN_TESTS = "--run-tests"

_log = logging.getLogger(__name__)


# TODO: add a version option -V that reads the package version number.

# We escape the leading "%" so that the leading "%p" is not interpreted as
# a Python string formatting conversion specifier.  The optparse.OptionParser
# class, however, recognizes "%prog" by replacing it with the current
# script name when passed to the constructor as a usage string.
USAGE = """%prog [options]

Create a new project from a Groom template.

This script creates a new project from a Groom project template using
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

    # We prevent the help option from being added automatically so that
    # we can add our own optional manually.  This lets us prevent exiting
    # when a help option is passed (e.g. "-h" or "--help").
    parser = OptionParser(usage=usage, add_help_option=False)

    # TODO: explicitly add a version option?
    parser.add_option("-g", "--groom-template", metavar='DIRECTORY', dest="project_directory",
                      action="store", type='string', default=defaults.source_root_directory,
                      help='the directory containing the groom project template.  '
                           'Defaults to the default template directory.')
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
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", default=False,
                      help="log verbosely.")
    parser.add_option("-e", "--expected", dest="should_generate_expected",
                      action="store_true", default=False,
                      help='whether to regenerate the "expected" version of each '
                           'project template.  Regenerating versions does not '
                           'delete files but only overwrites them.  This option '
                           'is exposed mainly for molt development purposes.')
    parser.add_option(OPTION_RUN_TESTS, dest="run_tests",
                      action="store_true", default=False,
                      help='whether to run tests.  Runs all available project tests.  '
                           'This includes all unit tests, all available doctests, '
                           'and, if available, the template directory test cases '
                           'on the Groom project web site.')
    parser.add_option("--test-output-dir", metavar='DIRECTORY',
                      dest="test_output_dir", action="store", default=None,
                      help='the directory to which to write test case output '
                           '(e.g. for groom tests).  '
                           'Defaults to a system temp location, in which case '
                           'the directory is always cleaned up.  '
                           'When this option is provided, only test case failures '
                           'are not cleaned up.  '
                           'This allows for examination of test case failures.')
    parser.add_option("-h", "--help", action=help_action,
                      help="show this help message and exit.")

    return parser


def preparse_args(sys_argv):
    """
    Parse command arguments without raising an exception (or exiting).

    This function allows one to have access to the command-line options
    before configuring logging (in particular before exception logging).

    Returns: the pair (options, args).

    """
    try:
        # Suppress the help option to prevent exiting.
        options, args = parse_args(sys_argv, suppress_help_exit=True)
    except UsageError:
        # Any usage error will occur again during the real parse.
        return None, None

    return options, args


def parse_args(sys_argv, suppress_help_exit, usage=None, defaults=None):
    """
    Parse arguments and return (options, args).

    Raises UsageError on command-line usage error.

    """
    if defaults is None:
        defaults = DefaultOptions()

    parser = create_parser(defaults, suppress_help_exit=suppress_help_exit, usage=usage)

    # The optparse module's parse_args() normally expects sys.argv[1:].
    args = sys_argv[1:]
    options, args = parser.parse_args(args)

    return options, args


def read_args(sys_argv, usage, defaults):
    """
    Raises UsageError on bad arguments.


    """
    options, args = parse_args(sys_argv, suppress_help_exit=False, usage=usage, defaults=defaults)

    _log.debug("Configuration file: %s" % options.config_path)
    _log.debug("Project directory: %s" % options.project_directory)
    _log.debug("Target directory: %s" % options.target_directory)

    return options

