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
Exposes default functionality.

"""

from __future__ import absolute_import

import os


_DEFAULT_ENCODING = 'utf-8'

FILE_ENCODING = _DEFAULT_ENCODING
LAMBDA_ENCODING = _DEFAULT_ENCODING
OUTPUT_FILE_ENCODING = _DEFAULT_ENCODING
ENCODING_ERRORS = 'strict'

_OUTPUT_PARENT_DIR = 'temp'
_OUTPUT_DIR_NAME = 'output'
_OUTPUT_DIR_NAME_DEMO = 'demo-template'

TEMPLATE_PROJECT_DIR_NAME = 'structure'
TEMPLATE_PARTIALS_DIR_NAME = 'partials'
TEMPLATE_LAMBDAS_DIR_NAME = 'lambdas'
TEMPLATE_EXPECTED_DIR_NAME = 'expected'

CONFIG_FILE_NAME = 'sample'  # without extension
CONFIG_FILE_EXTENSIONS = ['.json', '.yaml', '.yml']
CONFIG_CONTEXT_KEY = 'context'

# Names to pass to Python's filecmp.dircmp() for the `ignore` argument.
DIRCMP_IGNORE = ['.DS_Store', '__pycache__']

# For fuzzy equality testing in molt.diff.
FUZZY_MARKER = "..."

FORMAT_NEW_DIR = lambda dir_path, index: "%s_%s" % (dir_path, index)

OUTPUT_DIR = os.path.join(_OUTPUT_PARENT_DIR, _OUTPUT_DIR_NAME)
DEMO_OUTPUT_DIR = os.path.join(_OUTPUT_PARENT_DIR, _OUTPUT_DIR_NAME_DEMO)
