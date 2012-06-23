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
TODO: add a docstring.

"""

import os

ENCODING_DEFAULT = 'utf-8'
TEMP_EXTENSION = '.temp'


def read(path, encoding=None):
    """
    Read and return the contents of a text file as a unicode string.

    """
    if encoding is None:
        encoding = ENCODING_DEFAULT

    # This function implementation was chosen to be compatible across Python 2/3.
    with open(path, 'rb') as f:
        b = f.read()

    return b.decode(encoding)


def write(u, path, encoding=None):
    """
    Write a unicode string to a file (as utf-8).

    """
    if encoding is None:
        encoding = ENCODING_DEFAULT

    print("Writing to: %s" % path)
    # This function implementation was chosen to be compatible across Python 2/3.
    b = u.encode(encoding)
    with open(path, 'wb') as f:
        f.write(b)


def find_directories(root_dir):
    """
    Return a list of the directories inside dir_path, including dir_path.

    The function returns the directories as relative to the given directory.

    """
    dir_paths = ['']  # Start with root directory.
    for (dir_path, dir_names, filenames) in os.walk(root_dir):
        for dir_name in dir_names:
            path = os.path.join(dir_path, dir_name)
            path = os.path.relpath(path, root_dir)
            dir_paths.append(path)

    return dir_paths


def find_package_data(root_dir, file_globs):
    """
    Return the relative path names inside the given root directory.

    """
    dir_paths = find_directories(root_dir)

    paths = []
    for dir_path in dir_paths:
        for file_glob in file_globs:
            path = os.path.join(dir_path, file_glob)
            paths.append(path)

    return paths


def make_temp_path(path, new_ext=None):
    """
    Arguments:

      new_ext: the new file extension, including the leading dot.
        Defaults to preserving the file extension.

    """
    root, ext = os.path.splitext(path)
    if new_ext is None:
        new_ext = ext
    temp_path = root + TEMP_EXTENSION + new_ext

    return temp_path


def convert_md_to_rst(path, docstring_path):
    """
    Convert the given file from markdown to reStructuredText.

    Returns the new path.

    """
    target_path = make_temp_path(path, new_ext='.rst')
    print("Converting with pandoc: %s to %s" % (path, target_path))

    if os.path.exists(target_path):
        os.remove(target_path)

    # Pandoc uses the UTF-8 character encoding for both input and output.
    command = "pandoc --write=rst --output=%s %s" % (target_path, path)
    os.system(command)

    if not os.path.exists(target_path):
        s = ("Error running: %s\n"
             "  Did you install pandoc per the %s docstring?" % (command, docstring_path))
        sys.exit(s)

    return target_path