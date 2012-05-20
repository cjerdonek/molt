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

import molt
from molt import commandline
from molt.commandline import OPTION_OUTPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_DEMO_OUTPUT_DIR, get_version_string
from molt.common.common import get_demo_template_dir
from molt.common.error import Error
from molt.common.optionparser import UsageError
from molt.logconfig import configure_logging
from molt.render import Molter
from molt.test.harness.main import run_molt_tests
from molt.view import File


_log = logging.getLogger("main")

LOGGING_LEVEL_DEFAULT = logging.INFO

EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_FAIL = 1
EXIT_STATUS_USAGE_ERROR = 2

ENCODING_DEFAULT = 'utf-8'

OUTPUT_DIR_FORMAT = "%s (%s)"  # subsituted with (dir_path, index).


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


def create_demo(options):
    output_dir = options.output_directory
    if output_dir is None:
        output_dir = DEFAULT_DEMO_OUTPUT_DIR

    if os.path.exists(output_dir):
        s = """\
Output directory already exists: %s
You can specify a different output directory with %s.""" % (output_dir, OPTION_OUTPUT_DIR)
        raise Error(s)

    demo_template_dir = get_demo_template_dir()

    copytree(demo_template_dir, output_dir)
    _log.info("Created demo template directory: %s" % output_dir)

    return output_dir


def try_make_dir(dir_path):
    """
    Make the given directory and return whether successful.

    """
    try:
        os.mkdir(dir_path)
    except OSError:
        # Check for a fatal failure reason.
        parent_dir, name = os.path.split(dir_path)
        if parent_dir and not os.path.exists(parent_dir):
            raise Error("Directory does not exist: %s" % parent_dir)
        if not os.path.exists(dir_path):
            # Then there was an unanticipated failure reason.
            raise
        return False
    return True


def make_output_dir(dir_path):
    if try_make_dir(dir_path):
        return dir_path
    # Otherwise, we need to find an unused directory name.

    index = 1
    while True:
        new_path = OUTPUT_DIR_FORMAT % (dir_path, index)
        if try_make_dir(new_path):
            return new_path
        index += 1


def _render(options, args):
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

    config_name = 'sample'
    exts = ['json', 'yaml', 'yml']
    paths = [make_path("%s.%s" % (config_name, ext)) for ext in exts]
    for config_path in paths:
        if os.path.exists(config_path):
            break
    else:
        indent = "\n  "
        raise Error("Config file not found in a default location:%s%s" %
                    (indent, indent.join(paths)))

    partials_dir = make_path('partials')
    if not os.path.exists(partials_dir):
        partials_dir = None

    output_dir = options.output_directory
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir = make_output_dir(output_dir)

    render(project_dir=project_dir, partials_dir=partials_dir, config_path=config_path,
           output_dir=output_dir)

    return output_dir


def run_args(sys_argv):

    options, args = commandline.parse_args(sys_argv)

    if options.run_test_mode:
        # Do not print the result to standard out.
        return run_tests(options)

    if options.create_demo_mode:
        result = create_demo(options)
    elif options.version_mode:
        result = get_version_string()
    else:
        result = _render(options, args)

    if result is not None:
        print result

    return EXIT_STATUS_SUCCESS


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
    logging_level = LOGGING_LEVEL_DEFAULT
    is_running_tests = False

    # TODO: follow all of the recommendations here:
    # http://www.artima.com/weblogs/viewpost.jsp?thread=4829

    # Configure logging before parsing options for real.
    options, args = commandline.preparse_args(sys_argv)
    if options is not None:
        if options.verbose:
            logging_level = logging.DEBUG
        if options.run_test_mode:
            is_running_tests = True

    configure_logging(logging_level, test_config=is_running_tests)

    try:
        status = process_args(sys_argv)
    # TODO: include KeyboardInterrupt in the template version of this file.
    except UsageError as err:
        s = """\
Command-line usage error: %s

Pass -h or --help for help documentation and available options.""" % err
        _log.error(s)

        status = EXIT_STATUS_USAGE_ERROR
    except Error, err:
        _log.error(err)
        status = EXIT_STATUS_FAIL

    return status
