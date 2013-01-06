#!/usr/bin/env python
# coding: utf-8

"""
Standard Python setup script to support distribution-related tasks.


Releasing to PyPI
-----------------

This section contains instructions for project maintainers on how to
release a new version of this project to PyPI.

(1) Prepare the release.

Make sure the code is finalized and merged to master, and bump the version
number in the package __init__.py.  You can use the following convenience
command to help check that the right files are being included in the source
distribution:

    python setup.py --show-sdist sdist

(2) Update the reStructuredText long_description file.

Update the file containing the long_description argument to setup():

    python setup.py prep

and then check in the new version.  You must have pandoc installed to run
the command above:

    http://johnmacfarlane.net/pandoc/

It helps to review this auto-generated file on GitHub as a sanity check
prior to uploading.  PyPI attempts to convert this string to HTML
before displaying it on the PyPI project page.  If PyPI finds any
issues, it will render it instead as plain-text, which we do not want.
You can also check the file for warnings by running:

    $ python setup.py --long-description | rst2html.py --no-raw > temp.html

after installing Docutils (http://docutils.sourceforge.net/).

Also see:

  http://docs.python.org/dev/distutils/uploading.html#pypi-package-display
  http://bugs.python.org/issue15231


(3) Push to PyPI.  To release a new version to PyPI--

    http://pypi.python.org/pypi/molt

create a PyPI user account if you do not already have one.  The user account
will need permissions to push to PyPI.  A current "Package Index Owner"
can grant you those permissions.

When you have permissions, run the following:

    python setup.py publish

If you get an error like the following--

    Upload failed (401): You must be identified to edit package information

then add a file called .pypirc to your home directory with the following
contents:

    [server-login]
    username: <PyPI username>
    password: <PyPI password>

as described here, for example:

    http://docs.python.org/release/2.5.2/dist/pypirc.html

(4) Tag the release on GitHub.  Here are some commands for tagging.

List current tags:

    git tag -l -n3

Create an annotated tag:

    git tag -a -m "first tag" "v0.1.0"

Push a tag to GitHub:

    git push --tags cjerdonek v0.1.0

"""

import filecmp
import os
import shutil
import sys

from molt_setup import main as setup_lib
from molt_setup.main import (
    ENCODING_DEFAULT,
    convert_md_to_rst,
    describe_differences,
    get_version,
    make_temp_path,
    read,
    strip_html_comments,
    write,
    DistHelper,
)

py_version = sys.version_info

# We use setuptools/Distribute because distutils does not seem to support
# the following arguments to setUp().  Passing these arguments to
# setUp() causes a UserWarning to be displayed.
#
#  * entry_points
#  * install_requires
#
import setuptools as dist
setup = dist.setup


PACKAGE_NAME = 'molt'

FILE_ENCODING = ENCODING_DEFAULT

README_PATH = 'README.md'
HISTORY_PATH = 'HISTORY.md'
LONG_DESCRIPTION_PATH = 'setup_long_description.rst'

COMMAND_PREP = 'prep'
COMMAND_PUBLISH = 'publish'
COMMAND_SDIST = 'sdist'
COMMAND_UPLOAD = 'upload'

ARG_USE_2TO3 = 'use_2to3'

OPTION_SHOW_SDIST = '--show-sdist'

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: Implementation :: PyPy',
)

INSTALL_REQUIRES = [
    'pystache',
    'pyyaml',
]

# TODO: decide whether to use find_packages() instead.  I'm not sure that
#   find_packages() is available with distutils, for example.
# TODO: use ".".join(parts).
PACKAGES = [
    'molt',
    'molt.commands',
    'molt.commands.molt',
    'molt.general',
    # The following packages are only for testing.
    'molt.test',
    'molt.test.general',
    'molt.test.extra',
    'molt.test.harness',
    # We exclude the following deliberately to exclude them from the build
    # and to prevent them from being installed in site-packages, for example.
    #'molt_setup',
    #'molt_setup.test',
]

DATA_DIRS = [
    # TODO: make this more fine-grained so package_data is smaller.
    ('molt', ['demo', 'test/data']),
]

DATA_FILE_GLOBS = [
    '*.json',
    '*.mustache',
    '*.py',
    '*.sh',
    '*.txt',
]


# TODO: use the logging package.
def log(msg):
    print("%s: %s" % (PACKAGE_NAME, msg))


def make_description_file(target_path):
    """
    Generate the long_description needed for setup.py.

    The long description needs to be formatted as reStructuredText:

      http://docs.python.org/distutils/setupscript.html#additional-meta-data

    """
    readme_path = README_PATH

    md_ext = os.path.splitext(readme_path)[1]

    # Remove our HTML comments because PyPI does not allow it.
    # See the setup.py docstring for more info on this.
    readme_text = strip_html_comments(readme_path)
    history_text = strip_html_comments(HISTORY_PATH)

    sections = [readme_text, history_text]
    md_description = '\n\n'.join(sections)

    md_description_path = make_temp_path(LONG_DESCRIPTION_PATH, new_ext=md_ext)

    log('writing: %s' % md_description_path)
    write(md_description, md_description_path)

    temp_path = make_temp_path(LONG_DESCRIPTION_PATH)
    rst_description = convert_md_to_rst(source_path=md_description_path,
                                        target_path=temp_path,
                                        docstring_path=__file__)

    # Comments in reST begin with two dots.
    intro_text = """\
.. This file is auto-generated by setup.py for PyPI using pandoc, so this
.. file should not be edited.  Edits should go in the source files.
"""

    rst_description = '\n'.join([intro_text, rst_description])

    write(rst_description, target_path)


def prep():
    make_description_file(LONG_DESCRIPTION_PATH)


def publish(sys_argv):
    """
    Publish this package to PyPI (aka "the Cheeseshop").

    """
    description_path = LONG_DESCRIPTION_PATH
    temp_path = make_temp_path(description_path)
    make_description_file(temp_path)

    if not filecmp.cmp(temp_path, description_path, shallow=False):
        print("""\
Description file not up-to-date: %s
Run the following command and commit the changes--

    python setup.py %s
""" % (description_path, COMMAND_PREP))
        sys.exit()

    print("Description up-to-date: %s" % description_path)

    # Upload to PyPI.
    sys_argv.extend([COMMAND_SDIST, COMMAND_UPLOAD])
    run_setup(sys_argv)


# The purpose of this function is to follow the guidance suggested here:
#
#   http://packages.python.org/distribute/python3.html#note-on-compatibility-with-setuptools
#
# The guidance is for better compatibility when using setuptools (e.g. with
# earlier versions of Python 2) instead of Distribute, because of new
# keyword arguments to setup() that setuptools may not recognize.
def get_extra_args():
    """
    Return a dictionary of extra args to pass to setup().

    """
    extra = {}
    # TODO: it might be more correct to check whether we are using
    #   Distribute instead of setuptools, since use_2to3 doesn't take
    #   effect when using Python 2, even when using Distribute.
    if py_version >= (3, ):
        # Causes 2to3 to be run during the build step.
        extra[ARG_USE_2TO3] = True

    return extra


def get_long_description():
    path = LONG_DESCRIPTION_PATH
    try:
        long_description = read(path)
    except IOError:
        if not os.path.exists(path):
            raise Exception("Long-description file not found at: %s\n"
                            "  You must first run the command: %s\n"
                            "  See the docstring of this module for details." % (path, COMMAND_PREP))
        raise
    return long_description


def find_package_data():
    """
    Return the value to use for setup()'s package_data argument.

    """
    package_data = {}
    file_globs = DATA_FILE_GLOBS

    for package_name, rel_dirs in DATA_DIRS:
        paths = []
        for rel_dir in rel_dirs:
            paths += setup_lib.find_package_data(package_dir=package_name, rel_dir=rel_dir, file_globs=file_globs)

        package_data[package_name] = paths

    return package_data


def show_differences(package_version):
    """
    Display how the sdist differs from the project directory.

    """
    def ignore_in_project_dir(path):
        dir_path, base_name = os.path.split(path)
        if base_name.endswith('.pyc'):
            return True
        if base_name == '__pycache__':
            return True
        if base_name == '.DS_Store':
            return True
        return False

    helper = DistHelper(PACKAGE_NAME, package_version)
    sdist_path = helper.sdist_path()

    log("extracting: %s" % sdist_path)
    extracted_dir = helper.extract()

    log("showing differences with: %s" % extracted_dir)
    print(describe_differences(extracted_dir, os.curdir, ignore_right=ignore_in_project_dir))


def run_setup(sys_argv):
    """
    Call setup().

    """
    package_dir = os.path.join(os.path.dirname(__file__), PACKAGE_NAME)
    package_version = get_version(package_dir)
    log("read version: %s" % package_version)

    long_description = get_long_description()
    package_data = find_package_data()
    extra_args = get_extra_args()

    # Prevent accidental uploads to PyPI.
    if COMMAND_UPLOAD in [arg.lower() for arg in sys_argv]:
        answer = raw_input("Are you sure you want to upload to PyPI (yes/no)?")
        if answer != "yes":
            exit("Aborted: nothing uploaded")

    show_sdist = False
    if OPTION_SHOW_SDIST in sys_argv:
        show_sdist = True
        sys_argv.remove(OPTION_SHOW_SDIST)

    if ARG_USE_2TO3 in extra_args:
        log('including kwarg: %s: %s' % (ARG_USE_2TO3, extra_args[ARG_USE_2TO3]))

    # We exclude the following arguments since we are able to use a
    # corresponding Trove classifier instead:
    #
    #  * license
    #
    setup(name=PACKAGE_NAME,
          version=package_version,
          description='Mustache project templates using Python and Groome',
          long_description=long_description,
          keywords='project template mustache pystache groome',
          author='Chris Jerdonek',
          author_email='chris.jerdonek@gmail.com',
          url='http://cjerdonek.github.com/molt/',
          install_requires=INSTALL_REQUIRES,
          packages=PACKAGES,
          package_data=package_data,
          entry_points = {
            'console_scripts': [
                'molt=molt.commands.molt.main:main',
            ],
          },
          classifiers = CLASSIFIERS,
          **extra_args
    )

    if COMMAND_SDIST in sys_argv and show_sdist:
        log('running option: %s' % OPTION_SHOW_SDIST)
        show_differences(package_version)


def main(sys_argv):
    # TODO: include the following in a verbose mode.
    log("using: version %s of %s" % (repr(dist.__version__), repr(dist)))

    command = sys_argv[-1]

    if command == COMMAND_PUBLISH:
        sys_argv.pop()
        publish(sys_argv)
    elif command == COMMAND_PREP:
        prep()
    else:
        run_setup(sys_argv)


if __name__=='__main__':
    main(sys.argv)
