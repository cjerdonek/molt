#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (C) 2011 Chris Jerdonek. All rights reserved.
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
Runs all unit tests and doctests in the project.

"""

# TODO: unit test this module.

import os

import molt
from molt.test.alltest import run_all_tests


LIBRARY_PACKAGE_NAME = 'molt'
README_REL_PATH = 'README.md'  # relative to the project directory.
TEST_MODULE_PATTERN = '*_unittest.py'


def run_tests(verbose=False):
    """
    Run all project tests, and return a unittest.TestResult instance.

    """
    source_dir = os.path.dirname(molt.__file__)
    package_dir = os.path.join(source_dir, os.pardir)
    package_name = molt.__name__
    readme_path = os.path.join(package_dir, README_REL_PATH)
    doctest_paths = [readme_path]

    # TODO: pass verbosity via the caller of this function.
    test_result = run_all_tests(source_dir=source_dir,
                                unittest_module_pattern=TEST_MODULE_PATTERN,
                                module_name=package_name,
                                doctest_paths=doctest_paths,
                                verbose=verbose)
    return test_result
