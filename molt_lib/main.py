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

import logging
import sys

_log = logging.getLogger("molt")

# TODO: this should be part of the option-parsing code.
DEBUG_OPTION = "-v"


# TODO: make this testable.
def configure_logging(logging_level):
    """Configure logging."""
    logger = logging.getLogger()  # the root logger.

    stream = sys.stderr
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.setLevel(logging_level)
    logger.addHandler(handler)

    _log.debug("Debug logging enabled.")


class Error(Exception):
    """Base class for exceptions defined in this project."""
    pass


class UsageError(Error):
    """Exception class for command-line syntax errors."""
    pass


def do_program_body(sys_argv):
    # TODO
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
    args = sys_argv[1:]

    # Configure logging prior to parsing options.
    configure_logging(logging.DEBUG if DEBUG_OPTION in args else logging.INFO)

    try:
        try:
            process_args(sys_argv)
        except Error as err:
            _log.error(err)
            raise
    except UsageError as err:
        print "\nPass -h or --help for help documentation and available options."
        return 2
    except Error, err:
        return 1


