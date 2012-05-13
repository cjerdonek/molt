# encoding: utf-8
#
# Copyright (C) 2011 Chris Jerdonek. All rights reserved.
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


# TODO: make this testable.
# TODO: finish documenting this method.
def configure_logging(logging_level, sys_stderr=None, test_config=False):
    """
    Configure logging.

    If in test mode, configures a "black hole" log handler for the
    root logger to prevent the following message from being written while
    running tests:

      'No handlers could be found for logger...'

    It also prevents the handler from displaying any log messages by
    configuring it to write to os.devnull instead of sys.stderr.

    """
    if sys_stderr is None:
        sys_stderr = sys.stderr

    root_logger = logging.getLogger()  # the root logger.
    root_logger.setLevel(logging_level)

    if test_config:
        # Then swallow stdout.
        stream = open(os.devnull,"w")
        handler = logging.StreamHandler(stream)
        root_logger.addHandler(handler)
        # Configure this module's logger.
        logger = _log

    formatter = logging.Formatter("%(name)s: [%(levelname)s] %(message)s")

    stream = sys_stderr
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    _log.debug("Debug logging enabled.")

