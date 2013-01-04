# encoding: utf-8
#
# Copyright (C) 2011-2013 Chris Jerdonek. All rights reserved.
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
Contains argument-parsing code and command-line documentation.

"""

from __future__ import absolute_import

import argparse
import logging
import os
import sys

from molt import __version__
from molt.general.optionparser import Option, ArgParser, UsageError
from molt import defaults
from molt.dirutil import get_default_config_files, DirectoryChooser


_log = logging.getLogger(__name__)

METAVAR_INPUT_DIR = 'DIRECTORY'

OPTION_CHECK_EXPECTED = Option(('--check-output', ))
OPTION_HELP = Option(('-h', '--help'))
OPTION_LICENSE = Option(('--license', ))
OPTION_OUTPUT_DIR = Option(('-o', '--output-dir'))
OPTION_MODE_DEMO = Option(('--create-demo', ))
OPTION_MODE_TESTS = Option(('--run-tests', ))
OPTION_MODE_VISUALIZE = Option(('--visualize', ))
OPTION_SOURCE_DIR = Option(('--dev-source-dir', ))
OPTION_WITH_VISUALIZE = Option(('--with-visualize', ))
OPTION_VERBOSE = Option(('-v', '--verbose'))

# We escape the leading "%" so that the leading "%" is not interpreted as a
# Python string formatting conversion specifier.  The argparse.ArgumentParser
# class will do its own substition for "%(prog)s", etc.
USAGE = "%%(prog)s [options] [%s]" % METAVAR_INPUT_DIR

DESCRIPTION = """\
Render the Groome template directory in %(input_dir_metavar)s.

A Groome template is a Mustache-based template for a directory of files.
See the Groome web page for details on Groome templates:

  http://cjerdonek.github.com/groome/

Per the Groome guidelines, the script looks in the following locations
when rendering a Groome template directory.  For the directory structure,
the script looks for a directory named "%(project_dir)s" in the template
directory.  For the optional directories of partials and lambdas, the
script looks in the template directory for directories named "%(partials_dir)s"
and "%(lambdas_dir)s", respectively.

Also per the guidelines, for the rendering context, the script uses
the value of the key "%(context_key)s" in the input configuration file
containing the rendering context.

The script writes the name of the output directory to stdout when
complete.  This is useful, in particular, when the output directory written
to is different from that given by the user.""" % {
    'context_key': defaults.CONFIG_CONTEXT_KEY,
    'project_dir': defaults.TEMPLATE_PROJECT_DIR_NAME,
    'partials_dir': defaults.TEMPLATE_PARTIALS_DIR_NAME,
    'lambdas_dir': defaults.TEMPLATE_LAMBDAS_DIR_NAME,
    'input_dir_metavar': METAVAR_INPUT_DIR,
}

EPILOG = "This is version %s of Molt." % __version__

COPYRIGHT_LINE = "Copyright (C) 2011-2013 Chris Jerdonek. All rights reserved."

LICENSE_STRING = """\
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* The names of the copyright holders may not be used to endorse or promote
  products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


def _get_version_header():
    return "Molt %s" % __version__


def get_version_string():
    using_string = "Using: Python %s\n at %s" % (sys.version, sys.executable)
    s = "\n\n".join([_get_version_header(), using_string, COPYRIGHT_LINE])
    return s


def get_license_string():
    s = "\n\n".join([_get_version_header(), COPYRIGHT_LINE, LICENSE_STRING])
    return s


def preparse_args(sys_argv):
    """
    Parse command arguments without raising an exception (or exiting).

    This function allows one to have access to the command-line options
    before configuring logging (in particular before exception logging).

    Returns a Namespace object.

    """
    try:
        # Suppress the help option to prevent exiting.
        ns = parse_args(sys_argv, None, suppress_help_exit=True)
    except UsageError:
        # Any usage error will occur again during the real parse.
        return None
    return ns


def parse_args(sys_argv, chooser=None, suppress_help_exit=False, usage=None):
    """
    Parse arguments and return a Namespace object.

    Raises UsageError on command-line usage error.

    """
    parser = _create_parser(chooser, suppress_help_exit=suppress_help_exit,
                            usage=usage)
    namespace = Namespace()  # use our decorator.
    return parser.parse_args(sys_argv[1:], namespace=namespace)


def _create_parser(chooser, suppress_help_exit=False, usage=None):
    """
    Return an ArgParser for the program.

    """
    if chooser is None:
        chooser = DirectoryChooser()
    if usage is None:
        usage = USAGE
    parser = ArgParser(usage=usage,
                       description=DESCRIPTION,
                       epilog=EPILOG,
                       add_help=False,
                       # Preserves formatting of the description and epilog.
                       formatter_class=argparse.RawDescriptionHelpFormatter)

    # TODO: incorporate the METAVAR names into the help messages, as appropriate.
    # TODO: fix the help message.
    parser.add_argument('input_directory', metavar='DIRECTORY',
                        nargs='?', default=None,
                        help='the input directory if one is required.  '
                              'In most cases, this should be a path to a '
                              'Groome template directory.')
    # TODO: alignment.
    parser.add_argument(*OPTION_OUTPUT_DIR, metavar='DIRECTORY', dest='output_directory',
                      action='store', default=None,
                      help='the directory to use when an output directory is '
                           'required.  Defaults to %s.  If the output directory '
                           'already exists, then the directory name is incremented '
                           'until the resulting directory would be new.' % repr(defaults.OUTPUT_DIR))
    config_paths = get_default_config_files()
    parser.add_argument('-c', '--config-file', metavar='FILE', dest='config_path',
                      action='store', default=None,
                      help='the path to the configuration file containing '
                           'the rendering context to use.  '
                           'Defaults to looking in the template directory '
                           'in order for one of: %s' % ', '.join(config_paths))
    parser.add_argument(*OPTION_WITH_VISUALIZE, dest='with_visualize',
                      action='store_true', default=False,
                      help='run the %s option on the output directory '
                           'prior to printing the usual output to stdout.  '
                           'Useful for quickly visualizing script output.  '
                           'Also works with %s combined with %s.' %
                           (OPTION_MODE_VISUALIZE.display(' or '),
                            OPTION_MODE_TESTS.display(' or '),
                            OPTION_OUTPUT_DIR.display(' or ')))
    parser.add_argument(*OPTION_CHECK_EXPECTED, metavar='DIRECTORY',
                        dest='expected_dir', action='store', nargs='?',
                        default=None,
                        help='when rendering, checks whether the output '
                             'directory matches the contents of DIRECTORY.  '
                             'Writes the differences to stderr and reports '
                             'the result via the exit status.  DIRECTORY '
                             "defaults to the template\'s expected directory.")
    parser.add_argument(*OPTION_MODE_DEMO, dest='create_demo_mode',
                      action='store_true', default=False,
                      help='create a copy of the Molt demo template to play with, '
                           'instead of rendering a template directory.  '
                           'The demo illustrates most major features of Groome.  '
                           'The command writes the demo template to the directory '
                           'provided by the %s option or, if that option is not '
                           'provided, to %s.' %
                           (OPTION_OUTPUT_DIR.display(' or '), repr(defaults.DEMO_OUTPUT_DIR)))
    # The default is used here only if the option is not present.
    parser.add_argument(*OPTION_MODE_TESTS, metavar='NAME', dest='test_names',
                        nargs='*', default=None,
                         help='run project tests, instead of instead of rendering '
                              'a template directory.  '
                              'Tests include unit tests, doctests, and, if present, '
                              'Groome project test cases.  '
                              # Escape the %.
                              'If %%(metavar)s arguments are provided, then only tests '
                              'whose names begin with one of the strings are run.  '
                              'If the %s option is provided, '
                              'then test failure data is retained for inspection '
                              'in a subset of that directory.' % OPTION_OUTPUT_DIR.display(' or '))
    parser.add_argument(*OPTION_MODE_VISUALIZE, dest='visualize_mode',
                      action='store_true', default=False,
                      help='print to stdout in a human-readable format '
                           'the contents of all files in input directory %s, '
                           'instead of rendering a template directory.  '
                           'Uses `diff` under the hood.' %
                           METAVAR_INPUT_DIR)
    # This argument is the path to a source checkout or source distribution.
    # This lets one specify project resources not available in a package
    # build or install, when doing development testing.  Defaults to no
    # source directory.
    parser.add_argument(*OPTION_SOURCE_DIR, metavar='DIRECTORY', dest='source_dir',
                      action='store', default=None,
                      help=argparse.SUPPRESS)
    parser.add_argument(*OPTION_LICENSE, dest='license_mode',
                      action='store_true', default=False,
                      help='print license info to stdout.')
    parser.add_argument('-V', '--version', dest='version_mode',
                      action='store_true', default=False,
                      help='print version info to stdout.')
    parser.add_argument(*OPTION_VERBOSE, dest='verbose',
                      action='store_true', default=False,
                      help='log verbosely.')
    # We add help manually for more control.
    help_action = "store_true" if suppress_help_exit else "help"
    parser.add_argument(*OPTION_HELP, action=help_action,
                        help='show this help message and exit.')

    return parser


class Namespace(argparse.Namespace):

    """
    A decorator for argparse's Namespace.

    """

    @property
    def run_test_mode(self):
        """Return whether to run unit tests."""
        # In particular, an empty list of test names should return True.
        return not self.test_names is None

    @property
    def check_output(self):
        """Return whether to check the output directory."""
        return self.expected_dir is not None
