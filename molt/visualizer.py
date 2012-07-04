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
Exposes a function to visualize the contents of a directory.

"""

from __future__ import absolute_import

import sys

from molt.general.popen import chain_script
from molt.general.io import temp_directory

# diff -Nur path1 path2
# --- path1	1969-12-31 16:00:00.000000000 -0800
# +++ path2	2012-05-27 17:45:10.000000000 -0700
# @@ -0,0 +1 @@
# +baz
# diff -Nur path3 path4
# --- path3	1969-12-31 16:00:00.000000000 -0800
# +++ path4	2012-05-21 23:43:52.000000000 -0700
# @@ -0,0 +1 @@
# +{{bar}}


def visualize(target_dir):
    """
    Print the contents of a directory to stdout in a human-readable format.

    """
    handler = _LineHandler()

    with temp_directory() as empty_temp_dir:
        args = ['diff', '-Nur', empty_temp_dir, target_dir]
        chain_script(args, handler.handle)


class _LineHandler(object):

    def __init__(self):
        self.in_chunk = False

    def handle(self, line):
        if line.startswith('diff'):
            self.in_chunk = False
            return
        if line.startswith('---'):
            return
        if line.startswith('+++') and not self.in_chunk:
            self.in_chunk = True
            # Strip the timestamp on the right.
            line = line.rsplit('\t', 1)[0] + '\n'
        sys.stdout.write(line)

