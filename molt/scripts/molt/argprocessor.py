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
import shutil
from StringIO import StringIO
import sys
import tempfile

import molt
from molt.general.error import Error
from molt import constants
from molt import defaults
import molt.diff as diff
import molt.dirutil as dirutil
# TODO: eliminate these from ... imports.
from molt.dirutil import stage_template_dir, DirectoryChooser
from molt.molter import Molter
from molt.projectmap import Locator
from molt.scripts.molt import argparsing
import molt.scripts.molt.general.optionparser as optionparser
from molt.test.harness import test_logger as tlog
from molt.test.harness.main import run_molt_tests
from molt import visualizer

METAVAR_INPUT_DIR = argparsing.METAVAR_INPUT_DIR

_log = logging.getLogger(__name__)

ENCODING_DEFAULT = 'utf-8'


def visualize(dir_path):
    visualizer.visualize(dir_path)


# TODO: consider whether we can have argparse handle this logic.
def _get_input_dir(ns, desc):
    input_dir = ns.input_directory

    if input_dir is None:
        if isinstance(desc, optionparser.Option):
            desc = "when using %s" % desc.display("/")
        msg = ("Argument %s not provided.\n"
               " You must specify an input directory %s." %
               (METAVAR_INPUT_DIR, desc))
        raise optionparser.UsageError(msg)

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

    return dirutil.make_available_dir(output_dir)


def run_mode_create_demo(ns):
    # TODO: inject the locator instance instead of constructing it here.
    locator = Locator()
    demo_template_dir = locator.demo_template_dir

    output_dir = _make_output_directory(ns, defaults.DEMO_OUTPUT_DIR)

    # TODO: add a comment explaining why we call os.rmdir().
    os.rmdir(output_dir)
    stage_template_dir(demo_template_dir, output_dir)

    if ns.with_visualize:
        visualize(output_dir)

    _log.info("Created demo template directory: %s" % output_dir)

    return output_dir


def run_mode_render(ns, chooser):
    """Returns the output directory."""
    template_dir = _get_input_dir(ns, 'when rendering a template')
    config_path = ns.config_path
    output_dir = _make_output_directory(ns, defaults.OUTPUT_DIR)

    renderer = TemplateRenderer(chooser=chooser, template_dir=template_dir,
                                output_dir=output_dir, config_path=config_path)
    renderer.render()

    if ns.with_visualize:
        visualize(output_dir)

    return output_dir


def run_mode_visualize(ns):
    target_dir = _get_input_dir(ns, argparsing.OPTION_MODE_VISUALIZE)
    visualize(target_dir)

    return None  # no need to print anything more.


# TODO: check-output should support checking a rendered directory.
# In other words, to check an output directory, it shouldn't be
# necessary to have to render each time.  As a side benefit, this
# resolves the stdout/stderr question for this case.
def check_output(output_dir, expected_dir):
    """Return whether the output directory matches the expected."""
    print("output: %s\nexpected: %s" % (output_dir, expected_dir))
    # TODO: implement this.
    return True


# TODO: rename this to process() or process_args().
# TODO: incorporate this method into the ArgProcessor class.
def run_args(sys_argv, writer, chooser=None, test_runner_stream=None,
             from_source=False, stdout=None):
    exit_status = constants.EXIT_STATUS_SUCCESS  # return value
    if chooser is None:
        chooser = DirectoryChooser()
    if test_runner_stream is None:
        test_runner_stream = sys.stderr
    if stdout is None:
        stdout = sys.stdout

    ns = argparsing.parse_args(sys_argv, chooser)

    if ns.run_test_mode:
        # Run all tests if no test names provided.
        test_names = ns.test_names or None
        return run_mode_tests(ns, test_names=test_names, test_runner_stream=test_runner_stream,
                             from_source=from_source)

    processor = ArgProcessor(chooser=chooser, writer=writer)
    run = processor.make_runner(ns)

    # TODO: consider using add_mutually_exclusive_group() for these.
    # TODO: file an issue in Python's tracker to add to
    # add_mutually_exclusive_group support for title, etc.
    # TODO: rename the functions for running each mode to run_mode_*().
    # TODO: change the mode attribute names to "mode_*".
    # TODO: use "run" for all modes to avoid any if logic below.
    if run is not None:
        did_succeed, output = run()
        if not did_succeed:
            exit_status = constants.EXIT_STATUS_FAIL
    elif ns.create_demo_mode:
        output = run_mode_create_demo(ns)
    # TODO: add a check-dirs mode.
    elif ns.visualize_mode:
        output = run_mode_visualize(ns)
    elif ns.version_mode:
        output = argparsing.get_version_string()
    elif ns.license_mode:
        output = argparsing.get_license_string()
    else:
        output = run_mode_render(ns, chooser)

    # TODO: ensure that check_output raises an error if running in
    # a mode that doesn't create an ouput directory.
    if ns.check_output and not check_output(output, ns.expected_dir):
        exit_status = constants.EXIT_STATUS_FAIL

    if output is not None:
        stdout.write(output)
        if not output.endswith("\n"):
            stdout.write("\n")

    return exit_status


class ArgProcessor(object):

    def __init__(self, chooser, writer):
        self.chooser = chooser
        self.writer = writer

    def make_runner(self, ns):
        if ns.mode_check_template:
            template_dir = _get_input_dir(ns, argparsing.OPTION_CHECK_TEMPLATE)
            output_dir = ns.output_directory
            checker = TemplateChecker(chooser=self.chooser,
                                      template_dir=template_dir,
                                      output_dir=output_dir,
                                      writer=self.writer)
            return checker.check
        return None


# This class should not depend on the Namespace returned by parse_args().
class TemplateRenderer(object):

    def __init__(self, chooser, template_dir, output_dir, config_path=None):
        self.chooser = chooser
        self.config_path = config_path
        self.output_dir = output_dir
        self.template_dir = template_dir

    def render(self):
        molter = Molter(chooser=self.chooser)
        molter.molt(template_dir=self.template_dir,
                    output_dir=self.output_dir,
                    config_path=self.config_path)


# This class should not depend on the Namespace returned by parse_args().
class TemplateChecker(object):

    def __init__(self, chooser, template_dir, output_dir, writer):
        self.chooser = chooser
        self.output_dir = output_dir
        self.template_dir = template_dir
        self.writer = writer

    def _write(self, msg):
        # TODO: use the output log.
        self.writer.write(msg)

    # TODO: extract this into a separate helper function or class?
    # A helper would be useful for the --compare-dirs option that has
    # not yet been implemented.
    def _compare(self, actual_dir, expected_dir):
        comparer = diff.Comparer()
        return comparer.compare_dirs((actual_dir, expected_dir))

    def _check(self, output_dir):
        """Render and return whether the directories match."""
        chooser = self.chooser
        template_dir = self.template_dir
        renderer = TemplateRenderer(chooser=chooser, template_dir=template_dir,
                                    output_dir=output_dir)
        renderer.render()
        expected_dir = chooser.get_expected_dir(template_dir)
        does_match = self._compare(output_dir, expected_dir)
        return does_match

    def check(self):
        """
        Returns a (does_check, output_dir) pair.

        """
        output_dir = None
        does_match = True
        _given_output_dir = self.output_dir
        try:
            if _given_output_dir is None:
                output_dir = tempfile.mkdtemp()
            else:
                # Increment the output directory if necessary.
                output_dir = dirutil.make_available_dir(_given_output_dir)
            _log.debug("created output dir: %s" % output_dir)
            does_match = self._check(output_dir)
            if does_match:
                msg = "template okay!"
            else:
                msg = "template not okay :("
            self._write(msg)
        finally:
            if output_dir is None:
                # Then directory creation failed.
                pass
            elif _given_output_dir is None or does_match:
                _log.debug("deleting output dir: %s" % output_dir)
                shutil.rmtree(output_dir)
                output_dir = None
            else:
                _log.debug("leaving output dir: %s" % output_dir)
        return does_match, output_dir
