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
Supplies the main method for the `molt` command entry point.

This module is a wrapper around another main method.  We use this wrapper
to let us configure logging with minimal amount of code imported (in
particular, before importing the bulk of the molt package).  This lets
us log statements about conditional imports more easily (e.g. whether
yaml has loaded as a replacement for json, etc).  Otherwise, logging
would not get configured after all those imports have already taken place.

"""

from __future__ import absolute_import

import logging
import traceback

from molt import commandline
from molt.commandline import OPTION_HELP, OPTION_VERBOSE
from molt.common.error import Error
from molt.common.optionparser import UsageError
from molt import constants
from molt import logconfig


LOGGING_LEVEL_DEFAULT = logging.INFO

_log = logging.getLogger(__name__)


def log_error(details, verbose):
    if verbose:
        msg = traceback.format_exc()
    else:
        msg = """\
%s
Pass %s for the stack trace.""" % (details, OPTION_VERBOSE.display(' or '))
    _log.error(msg)


def configure_logging(sys_argv):
    """
    Configure logging and return whether to run in verbose mode.

    """
    logging_level = LOGGING_LEVEL_DEFAULT
    is_running_tests = False

    # TODO: follow all of the recommendations here:
    # http://www.artima.com/weblogs/viewpost.jsp?thread=4829

    # Configure logging before parsing options for real.
    options, args = commandline.preparse_args(sys_argv)
    if options is not None:
        # Then options parsed without error.
        if options.verbose:
            logging_level = logging.DEBUG
        if options.run_test_mode:
            is_running_tests = True

    logconfig.configure_logging(logging_level, test_config=is_running_tests)

    verbose = False if options is None else options.verbose

    return verbose


def run_molt(sys_argv, configure_logging=configure_logging, process_args=None):
    """
    Execute this script's main function, and return the exit status.

    Args:

      process_args: the function called within this method's try-except
        block and that accepts sys.argv as a single parameter.
        This parameter is exposed only for unit testing purposes.  It
        allows the function's exception handling logic to be tested
        more easily.

    """
    verbose = configure_logging(sys_argv)
    _log.debug("args: %s" % repr(sys_argv))

    try:
        if process_args is None:
            # See this module's docstring for an explanation of why
            # we do this import inside a function body.
            from molt.argprocessor import run_args
            process_args = run_args
        status = process_args(sys_argv)
    # TODO: include KeyboardInterrupt in the template version of this file.
    except UsageError as err:
        details = """\
Command-line usage error: %s

Pass %s for help documentation and available options.""" % (err, OPTION_HELP.display(' or '))
        log_error(details, verbose)
        status = constants.EXIT_STATUS_USAGE_ERROR
    except Error, err:
        log_error(err, verbose)
        status = constants.EXIT_STATUS_FAIL

    return status
