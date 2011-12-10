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
Supports render configuration.

"""

from __future__ import absolute_import

import codecs
import logging
import os

from . import io
from .common.equality import Equalable

_log = logging.getLogger(__name__)


# TODO: move this method elsewhere.
def read_render_config(path, encoding):
    data = io.unserialize_yaml_file(path, encoding)
    config = parse_config(data)
    return config


# TODO: put the make_* methods into a class for "parsing" config nodes.
def make_path_action(data):
    """
    Return a PathAction instance given a dictionary config node.

    Raises an Exception if data is None.

    """
    new_name = data.get('rename')
    is_executable = data.get('executable')

    return PathAction(new_name, is_executable)


def make_contents(data):
    contents = data.get('contents', [])
    key_values = contents.items()

    return key_values


def read_path_config_node(data):
    """
    Read a node of the path config tree.

    """
    pa = PathAction(data)

    contents = data.get('contents', [])
    child_key_values = contents.items()

    return path_action, child_key_values


def parse_path_config(path_config, root_dir, dir_name):
    accumulator = []
    stack = Stack(root_dir, dir_name, path_config)

    # We use an iterative approach with an accumulator to avoid a recursive
    # implementation.
    while True:
        next = stack.pop()
        if next is None:
            break
        path, path_action = next
        accumulator.append((path, path_action))

    return accumulator


def parse_config(data):
    context = data['context']
    project_label = context['script_name']

    path_config = data['path_config']
    path_actions = parse_path_config(path_config, "root", "dir")

    return RenderConfig(context, project_label, path_actions)


class PathAction(Equalable):

    def __init__(self, new_name, is_executable):
        self.new_name = None if new_name is None else str(new_name)
        self.is_executable = bool(is_executable)

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, repr(self.new_name), repr(self.is_executable))


class Stack(object):

    def __init__(self, root_dir, dir_name, node):
        # A list of lists of (dir_name, node) pairs.
        self.remaining = []

        child_pairs = [(dir_name, node)]
        self._stage(root_dir, child_pairs)

    def _stage(self, dir_name, child_pairs):
        pair = (dir_name, child_pairs)
        self.remaining.append(pair)

    def pop(self):
        """
        Return the next (path, path_action) pair.

        """
        remaining = self.remaining
        while True:
            if not remaining:
                return None
            child_pairs = remaining[-1][1]
            if not child_pairs:
                remaining.pop()
                continue
            child_pair = child_pairs.pop()
            break
        # Stage the new node.
        dir_name, node = child_pair
        path_action, child_pairs = parse_node(node)
        self._stage(dir_name, child_pairs)

        path = os.path.join(*[pair[0] for pair in remaining])

        return path, path_action


class RenderConfig(object):

    def __init__(self, context, project_label, path_actions):
        self.context = context
        self.project_label = project_label
        self.path_actions = path_actions


