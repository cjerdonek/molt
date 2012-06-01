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
Exposes a run_molt_tests() function to run all tests in this project.

"""

from datetime import datetime
import os
from shutil import rmtree
import sys
from tempfile import mkdtemp

import molt
from molt.test.harness import test_logger as _log
from molt.test.harness.alltest import run_tests
from molt.test.harness.templatetest import make_template_tests


README_REL_PATH = 'README.md'  # relative to the project directory.
IS_UNITTEST_MODULE = lambda name: name.endswith('_test')


def make_dir_prefix():
    dt = datetime.now()
    prefix = "testrun_%s" % dt.strftime("%Y%m%d-%H%M%S-")
    return prefix


def is_empty(dir_path):
    return not os.listdir(dir_path)


def make_test_run_dir(test_output_dir):
    """
    Create the test run directory and return its path.

    Arguments:

      test_output_dir: the directory in which to create the test run directory.
        Defaults to a system-specific temp directory.

    """
    prefix = make_dir_prefix()
    dir_path = mkdtemp(prefix=prefix, dir=test_output_dir)
    _log.info("created test run dir: %s" % dir_path)

    return dir_path


def _run_tests(test_run_dir, doctest_paths, verbose, test_runner_stream):
    # TODO: also add support for --quiet.
    verbosity = 2 if verbose else 1

    test_config = TestConfig(test_run_dir)

    test_result = run_tests(package=molt,
                            is_unittest_module=IS_UNITTEST_MODULE,
                            test_config=test_config,
                            doctest_paths=doctest_paths,
                            verbosity=verbosity,
                            test_runner_stream=test_runner_stream)
    return test_result


def run_molt_tests(verbose=False, test_output_dir=None, test_runner_stream=None):
    """
    Run all project tests, and return a unittest.TestResult instance.

    Arguments:

      test_output_dir: the directory in which to leave test expectation
        failures.  If None, test runs are written to a system temp
        directory and test expectation failures deleted.

      test_runner_stream: the stream object to pass to unittest.TextTestRunner.
        Defaults to sys.stderr.

    """
    _log.info("running tests")

    if test_runner_stream is None:
        test_runner_stream = sys.stderr

    source_dir = os.path.dirname(molt.__file__)
    package_dir = os.path.join(source_dir, os.pardir)
    readme_path = os.path.join(package_dir, README_REL_PATH)
    doctest_paths = [readme_path]

    if test_output_dir is not None and not os.path.exists(test_output_dir):
        _log.info("creating test output dir: %s" % test_output_dir)
        os.makedirs(test_output_dir)

    test_run_dir = make_test_run_dir(test_output_dir)

    try:
        test_result = _run_tests(test_run_dir, doctest_paths, verbose,
                                 test_runner_stream=test_runner_stream)
    finally:
        if test_output_dir is None or is_empty(test_run_dir):
            _log.info("cleaning up: deleting: %s" % test_run_dir)
            rmtree(test_run_dir)
            test_run_dir = None
        else:
            _log.info("test failures at: %s" % test_run_dir)

    return test_result, test_run_dir


class TestConfig(object):

    """
    A container for test configuration data for Molt test runs.

    """

    def __init__(self, test_run_dir):
        """
        Arguments:

          test_run_dir: the "sandbox" directory in which to write temporary
            test data (for example the output directory of rendering
            a Groom template directory to compare with an expected directory).

        """
        self.test_run_dir = test_run_dir
