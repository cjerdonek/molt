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
Exposes a run_tests() function to run all tests in this project.

"""

import os

import molt
from molt.test.harness.alltest import run_tests
from molt.test.harness.common import test_logger as _log
from molt.test.harness.groomtests import make_groom_tests


# TODO: replace this with a command-line specified directory.
#_OUTPUT_PARENT_DIR = 'temp'
_OUTPUT_PARENT_DIR = None

_SOURCE_DIR = os.path.dirname(molt.__file__)
_PROJECT_DIR = os.path.normpath(os.path.join(_SOURCE_DIR, os.pardir))
_GROOM_INPUT_DIR = os.path.join(_PROJECT_DIR, os.path.normpath('submodules/groom/tests'))

README_REL_PATH = 'README.md'  # relative to the project directory.
IS_UNITTEST_MODULE = lambda name: name.endswith('_test')


def run_molt_tests(verbose=False):
    """
    Run all project tests, and return a unittest.TestResult instance.

    """
    _log.info("running tests")

    source_dir = os.path.dirname(molt.__file__)
    package_dir = os.path.join(source_dir, os.pardir)
    readme_path = os.path.join(package_dir, README_REL_PATH)
    doctest_paths = [readme_path]

    # TODO: also add support for --quiet.
    verbosity = 2 if verbose else 1

    groom_tests = make_groom_tests(groom_input_dir=_GROOM_INPUT_DIR,
                                   output_parent_dir=_OUTPUT_PARENT_DIR)

    test_result = run_tests(package=molt,
                            is_unittest_module=IS_UNITTEST_MODULE,
                            extra_tests=groom_tests,
                            doctest_paths=doctest_paths,
                            verbosity=verbosity)
    return test_result
