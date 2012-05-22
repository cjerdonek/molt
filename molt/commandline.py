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
from molt.common.optionparser import Option, OptionParser, UsageError
from molt.defaults import DEFAULT_OUTPUT_DIR, DEFAULT_DEMO_OUTPUT_DIR


_log = logging.getLogger(__name__)

OPTION_HELP = Option(('-h', '--help'))
OPTION_LICENSE = Option(('--license', ))
OPTION_OUTPUT_DIR = Option(('-o', '--output-dir'))
OPTION_RUN_TESTS = Option(('--run-tests',))
OPTION_VERBOSE = Option(('-v', '--verbose'))

OPTPARSE_USAGE = """%prog [options] [DIRECTORY]

Create a new project from the Groom template in DIRECTORY.

This script creates a new project from a Groom project template using
values from a configuration file.

The script writes the output directory to stdout when complete."""

OPTPARSE_EPILOG = "This is version %s of Molt." % __version__

COPYRIGHT_LINE = "Copyright (C) 2011-2012 Chris Jerdonek. All rights reserved."

LICENSE_STRING = """\
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* The names of the copyright holders may not be used to endorse or promote
  products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


def option_to_string(option):
    return " or ".join(option)


def get_version_header():
    return "Molt %s" % __version__


def get_version_string():
    using_string = "Using: Python %s\n at %s" % (sys.version, sys.executable)
    s = "\n\n".join([get_version_header(), using_string, COPYRIGHT_LINE])
    return s


def get_license_string():
    s = "\n\n".join([get_version_header(), COPYRIGHT_LINE, LICENSE_STRING])
    return s


def create_parser(suppress_help_exit=False, usage=None):
    """
    Return an OptionParser for the program.

    """
    if usage is None:
        usage = OPTPARSE_USAGE

    help_action = "store_true" if suppress_help_exit else "help"

    # We prevent the help option from being added automatically so that
    # we can add our own optional manually.  This lets us prevent exiting
    # when a help option is passed (e.g. "-h" or "--help").
    parser = OptionParser(usage=usage,
                          epilog=OPTPARSE_EPILOG,
                          add_help_option=False)

    parser.add_option(*OPTION_OUTPUT_DIR, metavar='DIRECTORY', dest="output_directory",
                      action="store", type='string', default=None,
                      help='the directory to use when an output directory is '
                           'required.  Defaults to %s.  If the directory already '
                           'exists, then the directory name is incremented '
                           'until a new directory can be created.' % repr(DEFAULT_OUTPUT_DIR))
    parser.add_option("-c", "--config", metavar='FILE', dest="config_path",
                      action="store", type='string', default='TODO',
                      help='the path to the configuration file that contains, '
                           'for example, the values with which to populate the template.  '
                           'Defaults to the default configuration file.')
    parser.add_option("--create-demo", dest="create_demo_mode",
                      action="store_true", default=False,
                      help='create a Groom template to play with that demonstrates '
                           'most features of Groom.  '
                           'The command writes to the directory specified by the '
                           '%s option.  If not specified, the output directory '
                           'defaults to %s.' %
                           (OPTION_OUTPUT_DIR.display(' or '), repr(DEFAULT_DEMO_OUTPUT_DIR)))
    parser.add_option(*OPTION_RUN_TESTS, dest="run_test_mode",
                      action="store_true", default=False,
                      help='whether to run tests.  Runs all available project tests,  '
                           'including unit tests, doctests, and, if available, '
                           'the Groom project test cases.  If the %s option '
                           'is provided, then test failure data is written '
                           'to a subset of that directory.' % OPTION_OUTPUT_DIR.display(' or '))
    parser.add_option(*OPTION_LICENSE, dest="license_mode",
                      action="store_true", default=False,
                      help="display license info.")
    parser.add_option("-V", "--version", dest="version_mode",
                      action="store_true", default=False,
                      help="display version info.")
    parser.add_option(*OPTION_VERBOSE, dest="verbose",
                      action="store_true", default=False,
                      help="log verbosely.")
    parser.add_option(*OPTION_HELP, action=help_action,
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


def parse_args(sys_argv, suppress_help_exit=False, usage=None):
    """
    Parse arguments and return (options, args).

    Raises UsageError on command-line usage error.

    """
    parser = create_parser(suppress_help_exit=suppress_help_exit, usage=usage)

    # The optparse module's parse_args() normally expects sys.argv[1:].
    args = sys_argv[1:]
    options, args = parser.parse_args(args)

    return options, args
