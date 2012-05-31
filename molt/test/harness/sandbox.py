# encoding: utf-8
#
# Copyright (C) 2012 Chris Jerdonek. All rights reserved.
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
Exposes functionality for creating temp directories during test runs.

"""

from __future__ import absolute_import

from contextlib import contextmanager
import os
from shutil import rmtree


@contextmanager
def _test_dir_manager(dir_path):
    """
    Return a contextmanager that creates (and deletes) a sandbox directory.

    The directory is not deleted if an exception occurs in the with block.

    It can be used either as--

        with test_dir_manager(dir_path):
            # Execute test code.

    Or (taking advantage of yield)--

        def custom_sandbox_dir():
            special_path = make_special_path()
            return test_dir_manager(special_path)

        with custom_sandbox_dir() as dir_path:
            # Execute test code.

    """
    os.mkdir(dir_path)
    yield dir_path
    # We do not put rmtree() in a try-finally because we do not want to
    # delete the directory if an exception (e.g. a test failure) occurs
    # in the with block.
    #
    # Also, it is safe to use rmtree because we created the directory
    # ourselves above.  In other words, it does not contain anything
    # that we do not already know about.
    rmtree(dir_path)


def _sandbox_dir_manager(test_case, test_run_dir, suffix=None):
    """
    Return a sandbox directory contextmanager.

    Creates a directory using the test case to construct the
    directory name.

    """
    # TestCase.id() is the fully-qualified name of the method, e.g.--
    #   molt.test.dirchooser_test.GenerateOutputDirTestCase.test_foo
    case_id = test_case.id()
    parts = case_id.split(".")
    parts = parts[-2:]  # the class name and method name.

    if suffix is not None:
        parts.append(suffix)

    name = "_".join(parts)

    dir_path = os.path.join(test_run_dir, name)

    return _test_dir_manager(dir_path)


class SandBoxDirMixin(object):

    """
    A unittest.TestCase mixin that supports creating test directories.

    Using this mixin requires setting the test_config attribute to
    a TestConfig instance prior to running the tests.  This can
    be done during test loading (e.g. using the load_tests protocol).

    """

    def sandboxDir(self, suffix=None):
        test_run_dir = self.test_config.test_run_dir
        return _sandbox_dir_manager(self, test_run_dir, suffix)
