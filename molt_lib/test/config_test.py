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
Unit tests for config.py.

"""

from __future__ import absolute_import

import unittest

from .. import config

make_path_action = config.make_path_action
parse_path_config = config.parse_path_config
PathAction = config.PathAction


TestCase = unittest.TestCase


class MakePathActionTestCase(TestCase):

    """
    Test make_path_action().

    """

    def assertPathAction(self, data, expected):
        actual = make_path_action(data)
        self.assertEquals(actual, expected)

    def testNone(self):
        self.assertRaises(Exception, make_path_action, None)

    def testEmpty(self):
        self.assertPathAction({}, PathAction(None, False))
        self.assertPathAction({'rename': "foo", "executable": 1}, PathAction("foo", True))


class PathActionTestCase(TestCase):

    """
    Test PathAction class.

    """

    def testConstructor(self):
        # None arguments.
        pa = PathAction(None, None)
        self.assertTrue(pa.new_name is None)
        # Test converts executable to boolean.
        self.assertTrue(pa.is_executable is False)

        # Test converts name to string.
        self.assertEquals(PathAction(1, 1), PathAction("1", True))

    def testRepr(self):
        rep = lambda a, b: repr(PathAction(a, b))
        self.assertEquals(rep("foo", True), "PathAction('foo', True)")


class ParsePathConfigTestCase(TestCase):

    def testNone(self):
        node = None
        #config = parse_path_config(node, "a", "b")

        #self.assertEquals


        #action1 = PathAction("foo", True)
        #action2 = PathAction("foo", True)

        #self.assertEquals(action1.__dict__, action2.__dict__)


