# encoding: utf-8
#
# Copyright (C) 2011 John Doe.  All rights reserved.
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
Exposes an option parser that is a subclass of optparse.OptionParser.

"""

from __future__ import absolute_import

import logging
# The optparse module is deprecated in Python 2.7 in favor of argparse.
# However, argparse is not available in Python 2.6.
import optparse
import sys


_log = logging.getLogger(__name__)


class UsageError(Exception):
    """
    Exception class for command-line syntax errors.

    """
    pass


# We subclass optparse.OptionParser to customize the behavior of error().
# The base class's implementation of error() prints the usage string
# and exits with status code 2.
class OptionParser(optparse.OptionParser):

    def error(self, message):
        """
        Handle an error occurring while parsing command arguments.

        This method overrides the OptionParser base class's error().  The
        OptionParser class requires that this method either exit or raise
        an exception.

        """
        raise UsageError(message)

