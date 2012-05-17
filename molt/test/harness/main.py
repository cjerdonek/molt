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
from tempfile import mkdtemp

import molt
from molt.test.harness.alltest import run_tests
from molt.test.harness.common import test_logger as _log
from molt.test.harness.templatetest import make_template_tests


_SOURCE_DIR = os.path.dirname(molt.__file__)
_PROJECT_DIR = os.path.normpath(os.path.join(_SOURCE_DIR, os.pardir))
_GROOM_INPUT_DIR = os.path.join(_PROJECT_DIR, os.path.normpath('submodules/groom/tests'))

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

    """
    prefix = make_dir_prefix()
    dir_path = mkdtemp(prefix=prefix, dir=test_output_dir)
    _log.info("created test run dir: %s" % dir_path)

    return dir_path


def _run_tests(test_run_dir, doctest_paths, verbose):
    groom_tests = make_template_tests(test_group_name='Groom',
                                      groom_input_dir=_GROOM_INPUT_DIR,
                                      test_run_dir=test_run_dir)

    # TODO: also add support for --quiet.
    verbosity = 2 if verbose else 1


    test_result = run_tests(package=molt,
                            is_unittest_module=IS_UNITTEST_MODULE,
                            extra_tests=groom_tests,
                            doctest_paths=doctest_paths,
                            verbosity=verbosity)
    return test_result

def run_molt_tests(verbose=False, test_output_dir=None):
    """
    Run all project tests, and return a unittest.TestResult instance.

    Arguments:

      test_output_dir: the directory in which to leave test expectation
        failures.  If None, test expectation failures are deleted.

    """
    _log.info("running tests")

    source_dir = os.path.dirname(molt.__file__)
    package_dir = os.path.join(source_dir, os.pardir)
    readme_path = os.path.join(package_dir, README_REL_PATH)
    doctest_paths = [readme_path]

    if test_output_dir is not None and not os.path.exists(test_output_dir):
        _log.info("creating test output dir: %s" % test_output_dir)
        os.makedirs(test_output_dir)

    test_run_dir = make_test_run_dir(test_output_dir)

    try:
        test_result = _run_tests(test_run_dir, doctest_paths, verbose)
    finally:
        if test_output_dir is None or is_empty(test_run_dir):
            _log.info("cleaning up: deleting: %s" % test_run_dir)
            rmtree(test_run_dir)
        else:
            _log.info("test failures at: %s" % test_run_dir)

    return test_result
