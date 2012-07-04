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
Exposes a utility function to call a shell script as a Python function.

"""

from __future__ import absolute_import

from subprocess import Popen, PIPE, STDOUT

from molt.general.error import reraise


def chain_script(args, handle_line):
    """
    Run args and call handle_line() on each line of stdout.

    """
    # See these page for implementation comments:
    #   http://stackoverflow.com/questions/2804543/read-subprocess-stdout-line-by-line
    #   http://docs.python.org/library/functions.html#iter
    proc = Popen(args, stdout=PIPE)
    for line in iter(proc.stdout.readline, ''):
        handle_line(line)


# Default to shell=False because shell=True is strongly discouraged for
# security reasons.
def call_script(args, b=None, shell=False):
    """
    Call the script with the given bytes sent to stdin.

    Returns a triple (stdout, stderr, returncode).

    """
    # See this page:
    #   http://stackoverflow.com/questions/163542/python-how-do-i-pass-a-string-into-subprocess-popen-using-the-stdin-argument

    try:
        proc = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=shell,
                     universal_newlines=False)
    except Exception as err:
        reraise("Error opening process: %s" % repr(args))

    stdout_data, stderr_data = proc.communicate(input=b)
    return_code = proc.returncode

    return stdout_data, stderr_data, return_code
