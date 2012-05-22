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
Exposes a generic run_tests() function to run all tests in a project.

"""

from __future__ import absolute_import

from contextlib import contextmanager
import logging
import os

import molt.test


@contextmanager
def sandbox_dir(dir_path):
    """
    Return a contextmanager that creates (and deletes) a sandbox directory.

    The directory is not deleted if an exception occurs in the with block.

    It can be used as follows:

        with sandbox_dir(dir_path):
            # Execute test code.

    """
    os.mkdir(dir_path)
    yield dir_path
    # We do not delete the directory if an exception (e.g. a test failure)
    # occurs in the with block.  That is why we do not put rmdir()
    # inside the finally block of a try-finally construct.
    os.rmdir(dir_path)


class TestUtil(object):

    def __init__(self, test_run_dir):
        self.test_run_dir = test_run_dir

    def sandbox_dir(self, test_case, suffix=None):
        """
        Return a sandbox directory contextmanager.

        """
        name = test_case.__class__.__name__
        if suffix is not None:
            name += "_" + suffix

        dir_path = os.path.join(self.test_run_dir, name)

        return sandbox_dir(dir_path)
