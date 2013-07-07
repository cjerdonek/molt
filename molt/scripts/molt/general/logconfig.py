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
Supports logging configuration.

"""

from __future__ import absolute_import

import logging
import os
import sys

_log = logging.getLogger(__name__)


class RememberingStream(object):

    """
    A stream that "remembers" the last text sent to write().

    """

    def __init__(self, stream, last_text=''):
        self._stream = stream
        self._last_text = last_text

    def last_char(self):
        if self._last_text:
            return self._last_text[-1]

    def write(self, text):
        if not text:
            return
        self._stream.write(text)
        self._last_text = text

    # A flush() method is needed to be able to pass instances of this
    # class to unittest.TextTestRunner's constructor.
    def flush(self):
        self._stream.flush()

class _NewlineStreamHandler(logging.StreamHandler):

    """
    A logging handler that begins log messages with a newline if needed.

    This class is useful for preventing messages logged during test runs
    from displaying at the end of a line of dots "......".

    The stream attribute (i.e. the stream passed to this class's
    constructor) must implement stream.last_char().

    """

    def emit(self, record):
        if self.stream.last_char() != "\n":
            self.stream.write("\n")

        super(_NewlineStreamHandler, self).emit(record)


# TODO: make this testable.
# TODO: finish documenting this method.
def configure_logging(logging_level, stderr=None, names=None):
    """
    Configure logging.

    If in test mode, configures a "black hole" log handler for the
    root logger to prevent the following message from being written while
    running tests:

      'No handlers could be found for logger...'

    Arguments:

      names: logger name prefixes to allow through the root logger.  The
        empty string allows all names.

    """
    if stderr is None:
        stderr = sys.stderr

    configurer = LogConfigurer(stream=stderr)

    format = "%(name)s: [%(levelname)s] %(message)s"
    handler = configurer.make_handler(format)
    _filter = configurer.make_names_filter(names)
    handler.addFilter(_filter)

    root_log = logging.getLogger()
    root_log.setLevel(logging_level)
    root_log.addHandler(handler)

    _log.debug("Debug logging enabled.")


class _Filter(object):

    def __init__(self, func):
        self.filter = func


class LogConfigurer(object):

    def __init__(self, stream):
        self.stream = stream

    def make_handler(self, format_string):
        formatter = logging.Formatter(format_string)
        handler = _NewlineStreamHandler(self.stream)
        handler.setFormatter(formatter)
        return handler

    def make_names_filter(self, names):
        filters = [logging.Filter(name) for name in names]
        def filter_func(record):
            for filt in filters:
                if filt.filter(record) != 0:
                    return 1
            return 0
        return _Filter(filter_func)
