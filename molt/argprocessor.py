# encoding: utf-8
#
# Copyright (C) 2011-2013 Chris Jerdonek. All rights reserved.
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
from StringIO import StringIO
import sys

import molt
from molt import commandline
from molt.general.error import Error
from molt.general.optionparser import UsageError
from molt import constants
from molt import defaults
from molt.dirutil import make_available_dir, stage_template_dir, DirectoryChooser
from molt.molter import Molter
from molt.projectmap import Locator
from molt.test.harness import test_logger as tlog
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


# TODO: consider whether we can have argparse handle this logic.
def _get_input_dir(ns, mode_description):
    input_dir = ns.input_directory

    if input_dir is None:
        raise UsageError("Argument %s not provided.\n"
                         "  Input directory needed for %s." %
                         (METAVAR_INPUT_DIR, mode_description))

    if not os.path.exists(input_dir):
        raise Error("Input directory not found: %s" % input_dir)

    return input_dir


def run_mode_tests(ns, test_names, test_runner_stream, from_source):
    """
    Run project tests, and return the exit status to exit with.

    """
    # Suppress the display of standard out while tests are running.
    tlog.info("running tests: suppressing stdout; from_source: %s" % from_source)
    stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        test_result, test_run_dir = run_molt_tests(from_source,
                                                   verbose=ns.verbose,
                                                   source_dir=ns.source_dir,
                                                   test_names=test_names,
                                                   test_output_dir=ns.output_directory,
                                                   test_runner_stream=test_runner_stream)
    finally:
        sys.stdout = stdout

    if ns.with_visualize and test_run_dir is not None:
        visualize(test_run_dir)

    return constants.EXIT_STATUS_SUCCESS if test_result.wasSuccessful() else constants.EXIT_STATUS_FAIL


def _make_output_directory(ns, default_output_dir):
    output_dir = ns.output_directory
    if output_dir is None:
        output_dir = default_output_dir

    return make_available_dir(output_dir)


def run_mode_create_demo(ns):
    # TODO: inject the locator instance instead of constructing it here.
    locator = Locator()
    demo_template_dir = locator.demo_template_dir

    output_dir = _make_output_directory(ns, defaults.DEMO_OUTPUT_DIR)

    os.rmdir(output_dir)
    stage_template_dir(demo_template_dir, output_dir)

    if ns.with_visualize:
        visualize(output_dir)

    _log.info("Created demo template directory: %s" % output_dir)

    return output_dir


def run_mode_render(ns, chooser):
    template_dir = _get_input_dir(ns, 'template rendering')

    config_path = ns.config_path
    output_dir = _make_output_directory(ns, defaults.OUTPUT_DIR)

    molter = Molter(chooser=chooser)
    molter.molt(template_dir=template_dir,
                output_dir=output_dir,
                config_path=config_path)

    if ns.with_visualize:
        visualize(output_dir)

    return output_dir


def run_mode_visualize(ns):
    target_dir = _get_input_dir(ns, '%s option' % commandline.OPTION_MODE_VISUALIZE)
    visualize(target_dir)

    return None  # no need to print anything more.


def run_args(sys_argv, chooser=None, test_runner_stream=None, from_source=False):
    if chooser is None:
        chooser = DirectoryChooser()
    if test_runner_stream is None:
        test_runner_stream = sys.stderr

    ns = commandline.parse_args(sys_argv, chooser)

    if ns.run_test_mode:
        # Run all tests if no test names provided.
        test_names = ns.test_names or None
        return run_mode_tests(ns, test_names=test_names, test_runner_stream=test_runner_stream,
                             from_source=from_source)

    # TODO: rename the functions for running each mode to run_mode_*().
    if ns.create_demo_mode:
        result = run_mode_create_demo(ns)
    elif ns.visualize_mode:
        result = run_mode_visualize(ns)
    elif ns.version_mode:
        result = commandline.get_version_string()
    elif ns.license_mode:
        result = commandline.get_license_string()
    else:
        result = run_mode_render(ns, chooser)

    if result is not None:
        print result

    return constants.EXIT_STATUS_SUCCESS
