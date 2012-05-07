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
The master pystache view.

"""

from __future__ import absolute_import

from datetime import datetime
import logging
import sys

import pystache


_log = logging.getLogger(__name__)


def comment_python_line(line):
    if line:
        line = " " + line
    return "#" + line


def render(template, values):

    rendered = pystache.render(template, values)

    return rendered


# TODO: make separate views for README and license.
class File(object):

    def __init__(self, **kwargs):

        super(File, self).__init__(**kwargs)

    def title(self):
        def make_title(text):
            inner = render(text, self.context)
            return "%s\n%s" % (inner, "=" * len(inner))

        return make_title

    # TODO: shouldn't this be part of the View class, or be supported
    # by pystache.render()?
    def render_text(self, text):
        return pystache.Template(text, self).render()

    def comment(self):
        def make_comment(text):
            inner = self.render_text(text)
            lines = inner.split("\n")
            new_lines = []
            for line in lines:
                new_line = comment_python_line(line)
                new_lines.append(new_line)
            return "\n".join(new_lines)

        return make_comment

    def current_year(self):
        return datetime.now().year

