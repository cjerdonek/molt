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
Exposes package-wide constants.

The constants are divided roughly into (1) hard-coded values that will
never change, and (2) default values for values that the user can
specify through the application (e.g. using a command-line option).

"""

from __future__ import absolute_import

import os

import molt

# Constants

_SOURCE_DIR = os.path.dirname(molt.__file__)
_PROJECT_DIR = os.path.normpath(os.path.join(_SOURCE_DIR, os.pardir))

_DEMO_TEMPLATE_DIR = 'demo'  # relative to the source directory.
_DEMO_EXPECTED_DIR = 'test/data/demo'

DEMO_EXPECTED_DIR = os.path.join(_SOURCE_DIR, _DEMO_EXPECTED_DIR)
DEMO_TEMPLATE_DIR = os.path.join(_SOURCE_DIR, _DEMO_TEMPLATE_DIR)

GROOM_INPUT_DIR = os.path.join(PROJECT_DIR, os.path.normpath('sub/groom/tests'))

# Defaults

_DEFAULT_OUTPUT_PARENT_DIR = 'temp'
_DEFAULT_OUTPUT_DIR_NAME = 'output'
_DEFAULT_OUTPUT_DIR_NAME_DEMO = 'demo'

DEFAULT_OUTPUT_DIR = os.path.join(_OUTPUT_PARENT_DIR, _OUTPUT_DIR_NAME)
DEFAULT_DEMO_OUTPUT_DIR = os.path.join(_OUTPUT_PARENT_DIR, _OUTPUT_DIR_NAME_DEMO)
