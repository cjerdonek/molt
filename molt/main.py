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
import sys
import traceback

from molt import argparsing
from molt.argparsing import OPTION_HELP, OPTION_VERBOSE
from molt.general.error import Error
from molt.general.optionparser import UsageError
from molt import constants
from molt import logconfig
from molt.test.harness import test_logger


LOGGING_LEVEL_DEFAULT = logging.INFO

_app_log = logging.getLogger("molt.app")
_log = logging.getLogger(__name__)


class RememberingStream(object):

    """
    A stream that "remembers" the last text sent to write().

    """

    def __init__(self, stream, last_text=''):
        self._stream = stream
        self._last_text = last_text

    def last_char(self):
        if self._last_text:
            return self._last_text[-1]

    def write(self, text):
        if not text:
            return
        self._stream.write(text)
        self._last_text = text

    # A flush() method is needed to be able to pass instances of this
    # class to unittest.TextTestRunner's constructor.
    def flush(self):
        self._stream.flush()


def log_error(details, verbose):
    if verbose:
        msg = traceback.format_exc()
    else:
        msg = """\
%s
Pass %s for the stack trace.""" % (details, OPTION_VERBOSE.display(' or '))
    _log.error(msg)


def _configure_logging(sys_argv, sys_stderr=None):
    """
    Configure logging and return whether to run in verbose mode.

    """
    if sys_stderr is None:
        sys_stderr = sys.stderr

    logging_level = LOGGING_LEVEL_DEFAULT
    is_running_tests = False
    verbose = False

    # We pass a newline as last_text to prevent a newline from being added
    # before the first log message.
    stderr_stream = RememberingStream(sys_stderr, last_text='\n')

    # TODO: follow all of the recommendations here:
    # http://www.artima.com/weblogs/viewpost.jsp?thread=4829

    # Configure logging before parsing arguments for real.
    ns = argparsing.preparse_args(sys_argv)

    if ns is not None:
        # Then args parsed without error.
        verbose = ns.verbose
        if verbose:
            logging_level = logging.DEBUG
        if ns.run_test_mode:
            is_running_tests = True

    persistent_loggers = [_app_log, test_logger]

    logconfig.configure_logging(logging_level, persistent_loggers=persistent_loggers,
                                stderr_stream=stderr_stream, test_config=is_running_tests)

    return verbose, stderr_stream


def run_molt(sys_argv, from_source=False, configure_logging=_configure_logging,
             process_args=None, **kwargs):
    """
    Execute this script's main function, and return the exit status.

    Args:

      from_source: whether or not the script was initiated from a source
        checkout (e.g. by calling `python -m molt.commands.molt` as
        opposed to via an installed setup entry point).

      process_args: the function called within this method's try-except
        block and that accepts sys.argv as a single parameter.
        This parameter is exposed only for unit testing purposes.  It
        allows the function's exception handling logic to be tested
        more easily.

    """
    verbose, stderr_stream = configure_logging(sys_argv)

    _app_log.debug("sys.argv: %s" % repr(sys_argv))
    _app_log.debug("kwargs: %s" % repr(kwargs))

    try:
        if process_args is None:
            # See this module's docstring for an explanation of why
            # we do this import inside a function body.
            from molt.argprocessor import run_args
            process_args = run_args
        status = process_args(sys_argv, test_runner_stream=stderr_stream,
                              from_source=from_source)
    # TODO: include KeyboardInterrupt in the template version of this file.
    except UsageError as err:
        details = """\
Command-line usage error: %s
-->%s

Pass %s for help documentation and available options.""" % (
            err, repr(sys.argv), OPTION_HELP.display(' or '))
        log_error(details, verbose)
        status = constants.EXIT_STATUS_USAGE_ERROR
    except Error, err:
        log_error(err, verbose)
        status = constants.EXIT_STATUS_FAIL

    return status
