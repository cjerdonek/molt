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
Exposes wrapper functions for file IO.

"""

from __future__ import absolute_import

import codecs
from contextlib import contextmanager
import json
import logging
import os
from shutil import rmtree
from tempfile import mkdtemp

from molt.general.error import reraise


_log = logging.getLogger(__name__)

try:
    # We make it so that not having YAML is not fatal.
    import yaml
except ImportError, err:
    _log.debug("yaml not found: %s" % repr(err))


def read(path, encoding, errors):
    """
    Read and return the contents of a text file as a unicode string.

    """
    # This function implementation was chosen to be compatible across Python 2/3.
    with open(path, 'rb') as f:
        b = f.read()

    try:
        return b.decode(encoding, errors)
    except UnicodeDecodeError, err:
        reraise("path: %s" % path)


def write(u, path, encoding, errors):
    """
    Write a unicode string to a file.

    """
    b = u.encode(encoding=encoding, errors=errors)

    _log.info("Writing: %s" % repr(str(path)))
    with open(path, 'wb') as f:
        f.write(b)


def create_directory(path):
    """
    Create a directory if not there, and return whether one was created.

    """
    if not os.path.exists(path):
        os.mkdir(path)
        _log.info("Created directory: %s" % path)
        return True
    if os.path.isdir(path):
        return False
    raise Error("Path already exists and is not a directory: %s" % path)


@contextmanager
def temp_directory():
    """
    Return a contextmanager that creates and deletes a temp directory.

    The contextmanager deletes the directory even if an exception occurs
    in the with block.  It can be used as follows:

        with sandbox_dir() as dir_path:
            # Execute code.

    """
    dir_path = mkdtemp()

    try:
        yield dir_path
    finally:
        # It is safe to use rmtree because we created the directory
        # ourselves above, so it is not possible for us to be deleting
        # anything that existed before.
        rmtree(dir_path)


def deserialize(path, encoding, errors):
    """
    Deserialize a JSON or YAML file based on the file extension.

    """
    u = read(path, encoding, errors)

    ext = os.path.splitext(path)[1]

    if ext.startswith(".y"):  # e.g. ".yaml" or ".yml".
        return yaml.safe_load(u)
    return json.loads(u)


# TODO: combine with deserialize().
def unserialize_yaml_file(path, encoding):
    """
    Deserialize a yaml file.

    """
    with codecs.open(path, "r", encoding=encoding) as f:
        data = yaml.load(f)

    return data


