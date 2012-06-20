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
Provides the main sys.argv processing code, but without the try-catch.

"""

import codecs
from datetime import datetime
import logging
import os
from shutil import copytree
from StringIO import StringIO
import sys

import molt
from molt import commandline
from molt.common.error import Error
from molt.common.optionparser import UsageError
from molt import constants
from molt import defaults
from molt.dirchooser import make_output_dir, DirectoryChooser
from molt.molter import Molter
from molt.test.harness.main import run_molt_tests
from molt import visualizer

METAVAR_INPUT_DIR = commandline.METAVAR_INPUT_DIR

_log = logging.getLogger(__name__)

ENCODING_DEFAULT = 'utf-8'


def visualize(dir_path):
    visualizer.visualize(dir_path)


def log_error(details, verbose):
    if verbose:
        msg = traceback.format_exc()
    else:
        msg = """\
%s
Pass %s for the stack trace.""" % (details, OPTION_VERBOSE.display(' or '))
    _log.error(msg)


def _get_input_dir(options, args, mode_description):
    try:
        input_dir = args[0]
    except IndexError:
        raise UsageError("Argument %s not provided.\n"
                         "  Input directory needed for %s." %
                         (METAVAR_INPUT_DIR, mode_description))

    if not os.path.exists(input_dir):
        raise Error("Input directory not found: %s" % input_dir)

    return input_dir


def run_tests(options, test_runner_stream, extra_packages):
    """
    Run project tests, and return the exit status to exit with.

    Arguments:

      extra_packages: packages to test in addition to the main package.

    """
    # Suppress the display of standard out while tests are running.
    stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        test_result, test_run_dir = run_molt_tests(verbose=options.verbose,
                                                   extra_packages=extra_packages,
                                                   test_output_dir=options.output_directory,
                                                   test_runner_stream=test_runner_stream)
    finally:
        sys.stdout = stdout

    if options.with_visualize and test_run_dir is not None:
        visualize(test_run_dir)

    return constants.EXIT_STATUS_SUCCESS if test_result.wasSuccessful() else constants.EXIT_STATUS_FAIL


def _make_output_directory(options, default_output_dir):
    output_dir = options.output_directory
    return make_output_dir(output_dir, default_output_dir)


def create_demo(options):
    output_dir = _make_output_directory(options, defaults.DEMO_OUTPUT_DIR)

    os.rmdir(output_dir)
    copytree(constants.DEMO_TEMPLATE_DIR, output_dir)

    if options.with_visualize:
        visualize(output_dir)

    _log.info("Created demo template directory: %s" % output_dir)

    return output_dir


def _render(options, args, chooser):
    template_dir = _get_input_dir(options, args, 'template rendering')

    config_path = options.config_path
    output_dir = _make_output_directory(options, defaults.OUTPUT_DIR)

    molter = Molter(chooser=chooser)
    molter.molt(template_dir=template_dir,
                output_dir=output_dir,
                config_path=config_path)

    if options.with_visualize:
        visualize(output_dir)

    return output_dir


def run_visualize_mode(options, args):
    target_dir = _get_input_dir(options, args, '%s option' % commandline.OPTION_MODE_VISUALIZE)
    visualize(target_dir)

    return None  # no need to print anything more.


def run_args(sys_argv, chooser=None, test_runner_stream=None, extra_test_packages=None):
    """
    Arguments:

      extra_test_packages: packages to test in addition to the main package.
        Defaults to the empty list.

    """
    if chooser is None:
        chooser = DirectoryChooser()
    if test_runner_stream is None:
        test_runner_stream = sys.stderr
    if extra_test_packages is None:
        extra_test_packages=[]

    options, args = commandline.parse_args(sys_argv, chooser)

    if options.run_test_mode:
        # Do not print the result to standard out.
        return run_tests(options, test_runner_stream=test_runner_stream,
                         extra_packages=extra_test_packages)

    if options.create_demo_mode:
        result = create_demo(options)
    elif options.visualize_mode:
        result = run_visualize_mode(options, args)
    elif options.version_mode:
        result = commandline.get_version_string()
    elif options.license_mode:
        result = commandline.get_license_string()
    else:
        result = _render(options, args, chooser)

    if result is not None:
        print result

    return constants.EXIT_STATUS_SUCCESS
