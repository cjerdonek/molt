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
Supplies the main method for the molt project.

"""

from __future__ import absolute_import

import codecs
from datetime import datetime
import logging
import os
from shutil import copytree
from StringIO import StringIO
import sys
import traceback

import molt
from molt import commandline
from molt.commandline import OPTION_HELP, OPTION_VERBOSE
from molt.common.error import Error
from molt.common.optionparser import UsageError
from molt.constants import DEMO_TEMPLATE_DIR
from molt import defaults
from molt.dirchooser import make_output_dir, DirectoryChooser
from molt import logconfig
from molt.molter import Molter
from molt.test.harness.main import run_molt_tests


_log = logging.getLogger(__name__)

LOGGING_LEVEL_DEFAULT = logging.INFO

EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2

ENCODING_DEFAULT = 'utf-8'


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


def run_tests(options):
    """
    Run project tests, and return the exit status to exit with.

    """
    # Suppress the display of standard out while tests are running.
    stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        test_result = run_molt_tests(verbose=options.verbose, test_output_dir=options.output_directory)
    finally:
        sys.stdout = stdout

    return EXIT_STATUS_SUCCESS if test_result.wasSuccessful() else EXIT_STATUS_FAIL

def _make_output_directory(options, default_output_dir):
    output_dir = options.output_directory
    return make_output_dir(output_dir, default_output_dir)

def create_demo(options):
    output_dir = _make_output_directory(options, defaults.DEMO_OUTPUT_DIR)

    os.rmdir(output_dir)
    copytree(DEMO_TEMPLATE_DIR, output_dir)
    _log.info("Created demo template directory: %s" % output_dir)

    return output_dir


def _render(options, args, chooser):
    try:
        template_dir = args[0]
    except IndexError:
        raise UsageError("Template directory argument not provided.")

    if not os.path.exists(template_dir):
        raise Error("Template directory not found: %s" % template_dir)

    make_path = lambda base_name: os.path.join(template_dir, base_name)

    project_dir = make_path('project')
    if not os.path.exists(project_dir):
        raise Error("Project directory not found: %s" % project_dir)

    partials_dir = make_path('partials')
    if not os.path.exists(partials_dir):
        partials = None

    config_path = chooser.get_config_path(options.config_path, template_dir)

    raise Exception("config: %s" % config_path)

    partials_dir = make_path('partials')
    if not os.path.exists(partials_dir):
        partials_dir = None

    output_dir = _make_output_directory(options, defaults.OUTPUT_DIR)

    molter = Molter()
    molter.molt(project_dir=project_dir, partials_dir=partials_dir, config_path=config_path,
                output_dir=output_dir)

    return output_dir


def run_args(sys_argv, chooser=None):
    if chooser is None:
        chooser = DirectoryChooser()

    options, args = commandline.parse_args(sys_argv, chooser)

    if options.run_test_mode:
        # Do not print the result to standard out.
        return run_tests(options)

    if options.create_demo_mode:
        result = create_demo(options)
    elif options.version_mode:
        result = commandline.get_version_string()
    elif options.license_mode:
        result = commandline.get_license_string()
    else:
        result = _render(options, args, chooser)

    if result is not None:
        print result

    return EXIT_STATUS_SUCCESS


def log_error(details, verbose):
    if verbose:
        msg = traceback.format_exc()
    else:
        msg = """\
%s
Pass %s for the stack trace.""" % (details, OPTION_VERBOSE.display(' or '))
    _log.error(msg)


def run_molt(sys_argv, configure_logging=configure_logging, process_args=run_args):
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
        status = process_args(sys_argv)
    # TODO: include KeyboardInterrupt in the template version of this file.
    except UsageError as err:
        details = """\
Command-line usage error: %s

Pass %s for help documentation and available options.""" % (err, OPTION_HELP.display(' or '))
        log_error(details, verbose)
        status = EXIT_STATUS_USAGE_ERROR
    except Error, err:
        log_error(err, verbose)
        status = EXIT_STATUS_FAIL

    return status
