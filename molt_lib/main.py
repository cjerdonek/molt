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

import logging
import sys

from .optionparser import OptionParser
from .optionparser import UsageError


_log = logging.getLogger("main")


# TODO: add a version option -V that reads the package version number.

# We escape the leading "%" so that the leading "%p" is not interpreted as
# a Python string formatting conversion specifier.  The optparse.OptionParser
# class, however, recognizes "%prog" by replacing it with the current
# script name when passed to the constructor as a usage string.
# TODO: find out if OptionParser recognizes other strings.
# TODO: find the preferred way of writing the first line of the usage string.
USAGE = """%prog template_directory [config_file] [options]

Create a new Python project.

This script creates a Python project from a template in the given template
directory using values from the given configuration file.  If you do not
provide a configuration file, the script uses default values."""


class Error(Exception):
    """Base class for exceptions defined in this project."""
    pass


# TODO: make this testable.
def configure_logging(logging_level, sys_stderr=None):
    """Configure logging."""
    if sys_stderr is None:
        sys_stderr = sys.stderr

    logger = logging.getLogger()  # the root logger.

    logger.setLevel(logging_level)

    stream = sys_stderr
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _log.debug("Debug logging enabled.")


def create_parser(usage, include_help_option):
    """
    Return an OptionParser for the program.

    """
    parser = OptionParser(usage=usage, add_help_option=include_help_option)

    parser.add_option("-d", "--destination", metavar='DIRECTORY', dest="destination",
                      action="store", type='string', default=None,
                      help='the directory in which to create the new project. '
                           'Defaults to the current working directory.')
    parser.add_option("-v", dest="verbose", action="store_true",
                      help="log verbosely")

    return parser


def parse_args(sys_argv, usage=None, include_help_option=True):
    """
    Parse arguments and return (options, args).

    Raises UsageError on command-line usage error.

    """
    args = sys_argv[1:]

    parser = create_parser(usage, include_help_option)
    options, args = parser.parse_args(args)

    return options, args


def do_program_body(sys_argv, usage):
    options, args = parse_args(sys_argv, usage)
    print "Program body..."


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

    logging_level = logging.INFO

    try:
        # Do a first pass of option parsing just to determine the logging level.
        # Also, suppress display of the help string this time around.
        options, args = parse_args(sys_argv, include_help_option=False)
        if options.verbose:
            logging_level = logging.DEBUG
    except UsageError:
        pass

    # Configure logging prior to parsing options for real.
    configure_logging(logging_level)

    try:
        process_args(sys_argv, USAGE)
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


