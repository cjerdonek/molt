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
Contains the command-line documenation and command-line parsing code.

"""

from __future__ import absolute_import

import logging
import os
import sys

from molt import __version__
# TODO: use argparse instead of optparse:
#   http://docs.python.org/library/argparse.html#module-argparse
from .common.optionparser import OptionParser
from .common.optionparser import UsageError


_log = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_DEMO_OUTPUT_DIR = "molt-demo"

OPTION_OUTPUT_DIR = "--output-dir"
OPTION_RUN_TESTS = "--run-tests"

# TODO: move the version number to the end of the help text.  This probably
#   requires hacking optparse or using argparse.

# We escape the leading "%" so that the leading "%p" is not interpreted as
# a Python string formatting conversion specifier.  The optparse.OptionParser
# class, however, recognizes "%prog" by replacing it with the current
# script name when passed to the constructor as a usage string.
USAGE = """%%prog [options] [DIRECTORY]

Create a new project from a Groom template in DIRECTORY.

This script creates a new project from a Groom project template using
values from a configuration file.  It prints the output directory to
standard output when complete.

This is version %(version)s of Molt.""" % {'version': __version__}


def get_version_string():
    # TODO: move copyright string to a central location.
    # TODO: add license info to end.
    s = """\
Molt %(version)s

Using: Python %(sys_version)s
 at %(sys_executable)s

Copyright (C) 2011-2012 Chris Jerdonek.""" % {
    'version': __version__,
    'sys_executable': sys.executable,
    'sys_version': sys.version,
}

    return s

class DefaultOptions(object):
    """
    The default values that the OptionParser should use.

    """
    def __init__(self):
        self.config_path = ""
        self.destination_directory = ""
        self.source_root_directory = ""


def create_parser(defaults, suppress_help_exit=False, usage=USAGE):
    """
    Return an OptionParser for the program.

    """
    help_action = "store_true" if suppress_help_exit else "help"

    # We prevent the help option from being added automatically so that
    # we can add our own optional manually.  This lets us prevent exiting
    # when a help option is passed (e.g. "-h" or "--help").
    parser = OptionParser(usage=usage, add_help_option=False)

    # TODO: explicitly add a version option.
    parser.add_option("-o", OPTION_OUTPUT_DIR, metavar='DIRECTORY', dest="output_directory",
                      action="store", type='string', default=None,
                      help='the directory to which to write the new project. '
                           'Defaults to the directory %s.  If the directory '
                           'already exists, then the directory name is incremented '
                           'until a new directory can be created.  '
                           'The script writes the output directory to stdout '
                           'when complete.' % repr(DEFAULT_OUTPUT_DIR))
    parser.add_option("-c", "--config", metavar='FILE', dest="config_path",
                      action="store", type='string', default=defaults.config_path,
                      help='the path to the configuration file that contains, '
                           'for example, the values with which to populate the template.  '
                           'Defaults to the default configuration file.')
    parser.add_option("--overwrite", dest="should_overwrite",
                      action="store_true", default=False,
                      help='whether to permit files in the output directory to be '
                           'overwritten if the output directory already exists.')
    parser.add_option(OPTION_RUN_TESTS, dest="run_test_mode",
                      action="store_true", default=False,
                      help='whether to run tests.  Runs all available project tests,  '
                           'including unit tests, doctests, and, if available, '
                           'the Groom project test cases.  If the %s option '
                           'is provided, then test failure data is written '
                           'to a subset of that directory.')
    parser.add_option("--create-demo", dest="create_demo_mode",
                      action="store_true", default=False,
                      help='create a Groom template directory to play with.  '
                           'The directory outputs to %s.  If not specified, '
                           'the output directory defaults to %s.' % (OPTION_OUTPUT_DIR, DEFAULT_DEMO_OUTPUT_DIR))
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", default=False,
                      help="log verbosely.")
    parser.add_option("-V", "--version", dest="version_mode",
                      action="store_true", default=False,
                      help="display version info.")
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


def parse_args(sys_argv, suppress_help_exit=False, usage=None, defaults=None):
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
    _log.debug("Output directory: %s" % options.output_directory)

    return options

