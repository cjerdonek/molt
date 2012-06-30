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

from filecmp import dircmp
import os
import tarfile

ENCODING_UTF8 = 'utf-8'
ENCODING_DEFAULT = ENCODING_UTF8
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


def make_temp_dir(base_dir):
    """
    Create and return a temp directory.

    """
    i = 0
    target_dir = base_dir
    while True:
        try:
            os.mkdir(target_dir)
            break
        except OSError:
            if not os.path.exists(target_dir):
                # Then there was some other kind of error that we can't handle.
                raise
        i += 1
        target_dir = "%s (%s)" % (base_dir, i)

    return target_dir


class DistHelper(object):

    def __init__(self, package_name, version, dist_dir='dist', extracted_name='extracted'):
        self.dist_dir = dist_dir
        self.extracted_name = extracted_name
        self.package_name = package_name
        self.version = version

    def sdist_base_name(self):
        return "%s-%s" % (self.package_name, self.version)

    def sdist_file_name(self):
        return "%s.tar.gz" % self.sdist_base_name()

    def sdist_path(self):
        return os.path.join(self.dist_dir, self.sdist_file_name())

    def _extract(self, target_dir):
        """
        Extract the sdist, and return the directory to which it extracted.

        """
        unextracted_path = self.sdist_path()
        base_name = self.sdist_base_name()

        with tarfile.open(unextracted_path) as tar:
            tar.extractall(target_dir)

        return os.path.join(target_dir, base_name)

    def extract(self):
        """
        Extract the sdist, and return the directory to which it extracted.

        """
        base_temp_dir = os.path.join(self.dist_dir, self.extracted_name)
        temp_dir = make_temp_dir(base_temp_dir)
        extracted_dir = self._extract(temp_dir)

        return extracted_dir


# TODO: make this recursive.
def describe_difference(tar_path, project_dir, indent='  '):
    """
    Return a string describing the difference between the given directories.

    """
    def format(header, elements):
        if not elements:
            return ''
        strings = ['%s:' % header] + sorted(elements)
        glue = '\n' + indent

        return glue.join(strings)

    dcmp = dircmp(tar_path, project_dir)

    strings = [format('Only in %s' % tar_path, dcmp.left_only),
               format('Only in %s' % project_dir, dcmp.right_only),
               format('Differing', dcmp.diff_files)]

    return "\n".join(strings)


def walk_dir(top_dir, exclude_files=False, ignore=None):
    """
    Return a list of the paths inside the given directory.

    The function returns the paths as relative to the given directory
    and excludes the directory itself.

    """
    if ignore is None:
        ignore = lambda path: path.startswith('.')

    dir_paths = []
    for (dir_path, dir_names, file_names) in os.walk(top_dir):
        base_names = dir_names
        if not exclude_files:
            base_names += file_names

        for base_name in base_names:
            if ignore(base_name):
                # Ignore hidden files.
                continue
            path = os.path.join(dir_path, base_name)
            path = os.path.relpath(path, top_dir)
            dir_paths.append(path)

    dir_paths.sort()

    return dir_paths


def _find_rel_package_data(root_dir, file_globs):
    """
    Return the relative path names inside the given root directory.

    """
    dir_paths = walk_dir(root_dir, exclude_files=True)
    dir_paths.insert(0, '')

    paths = []
    for dir_path in dir_paths:
        for file_glob in file_globs:
            path = os.path.join(dir_path, file_glob)
            paths.append(path)

    return paths


def find_package_data(package_dir, rel_dir, file_globs):
    """
    Return the package_data paths for a directory inside a package.

    """
    data_dir = os.path.join(package_dir, rel_dir)

    paths = _find_rel_package_data(data_dir, file_globs)

    # package_data paths are interpreted as relative to the package directory.
    paths = [os.path.join(rel_dir, path) for path in paths]

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


def _convert_md_to_rst(path, docstring_path):
    """
    Convert the given file from markdown to reStructuredText.

    Returns the path to a UTF-8 encoded file.

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


def convert_md_to_rst(path, docstring_path):
    """
    Convert the file contents from markdown to reStructuredText.

    Returns the converted contents as a unicode string.

    Arguments:

      path: the path to the UTF-8 encoded file to be converted.

      docstring_path: the path to the Python file whose docstring contains
        instructions on how to install pandoc.

    """
    rst_path = _convert_md_to_rst(path, __file__)

    return read(rst_path, encoding=ENCODING_UTF8)
