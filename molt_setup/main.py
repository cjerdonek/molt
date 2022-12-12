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

    print("writing to: %s" % path)
    # This function implementation was chosen to be compatible across Python 2/3.
    b = u.encode(encoding)
    with open(path, 'wb') as f:
        f.write(b)


# This function lets us keep things more DRY.  See this e-mail exchange
# for a brief discussion, for example:
#   http://mail.python.org/pipermail/python-porting/2012-May/000298.html
def get_version(package_dir):
    """
    Parse the version string from a package.

    """
    init_path = os.path.join(package_dir, '__init__.py')
    text = read(init_path)

    needle = '__version__ ='
    try:
        line = next(line for line in text.splitlines() if line.startswith(needle))
    except StopIteration:
        raise Exception("version string not found in: %s" % init_path)

    expr = line[len(needle):]
    # Using eval() is more robust than using a regular expression.
    # For example, this method can handle single and double quotes,
    # end-of-line comments, and more complex version string expressions.
    version = eval(expr)

    return version


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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, target_dir)

        return os.path.join(target_dir, base_name)

    def extract(self):
        """
        Extract the sdist, and return the directory to which it extracted.

        """
        base_temp_dir = os.path.join(self.dist_dir, self.extracted_name)
        temp_dir = make_temp_dir(base_temp_dir)
        extracted_dir = self._extract(temp_dir)

        return extracted_dir


def _get_diff_paths(dir_path1, dir_path2, results, rel_parent_dir='', ignore=None):
    """
    Recursively examine the given directories, and modify results in place.

    Arguments:

      results: a three-tuple of (left_only, right_only, diff_files).

    """
    if ignore is None:
        ignore = lambda path: False

    rewrite_name = lambda name: os.path.join(rel_parent_dir, name)

    def get_relative(names):
        return [rewrite_name(name) for name in names if not ignore(name)]

    dcmp = dircmp(dir_path1, dir_path2)

    results[0].extend(get_relative(dcmp.left_only))
    results[1].extend(get_relative(dcmp.right_only))
    results[2].extend(get_relative(dcmp.diff_files))

    for dir_name in dcmp.common_dirs:
        dir1 = os.path.join(dir_path1, dir_name)
        dir2 = os.path.join(dir_path2, dir_name)
        new_rel_dir = rewrite_name(dir_name)

        _get_diff_paths(dir1, dir2, results, ignore=ignore, rel_parent_dir=new_rel_dir)


def describe_differences(dir_path1, dir_path2, ignore_right=None, indent='  '):
    """
    Return a string describing the difference between the given directories.

    Arguments:

      ignore_right: a function that accepts a relative path and returns
        whether to skip that path in the right-only list.

    """
    if ignore_right is None:
        ignore_right = lambda path: False

    def format(header, elements):
        header = '%s:' % header
        if not elements:
            header += " none"
        strings = [header] + sorted(elements)
        glue = '\n' + indent

        return glue.join(strings)

    # The 3-tuple is (left_only, right_only, diff_files).
    results = tuple([] for i in range(3))

    _get_diff_paths(dir_path1, dir_path2, results)

    right_only = results[1]
    # Slice notation modifies the list in place.
    right_only[:] = filter(lambda path: not ignore_right(path), right_only)

    headers = ['Only in %s' % dir_path1,
               'Only in %s' % dir_path2,
               'Differing']

    strings = [format(header, sorted(paths)) for header, paths in zip(headers, results)]

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


def strip_html_comments(source_path):
    """
    Read the file, and strip HTML comments.

    Returns a unicode string.

    """
    text = read(source_path)
    lines = text.splitlines(True)  # preserve line endings.

    # Remove HTML comments (which we only allow to take a special form).
    new_lines = filter(lambda line: not line.startswith("<!--"), lines)

    return "".join(new_lines)


def _convert_md_to_rst(source_path, target_path, docstring_path):
    """
    Convert the given file from markdown to reStructuredText.

    Returns the path to a UTF-8 encoded file.

    """
    # Pandoc uses the UTF-8 character encoding for both input and output.
    command = "pandoc --write=rst --output=%s %s" % (target_path, source_path)
    print("converting with pandoc: %s to %s\n-->%s" % (source_path, target_path, command))

    if os.path.exists(target_path):
        os.remove(target_path)

    os.system(command)

    if not os.path.exists(target_path):
        s = ("Error running: %s\n"
             "  Did you install pandoc per the %s docstring?" % (command, docstring_path))
        sys.exit(s)

    return target_path


def convert_md_to_rst(source_path, target_path, docstring_path):
    """
    Convert the file contents from markdown to reStructuredText.

    Returns the converted contents as a unicode string.

    Arguments:

      path: the path to the UTF-8 encoded file to be converted.

      docstring_path: the path to the Python file whose docstring contains
        instructions on how to install pandoc.

    """
    rst_path = _convert_md_to_rst(source_path, target_path, __file__)

    return read(rst_path, encoding=ENCODING_UTF8)
