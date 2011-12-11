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

from pprint import pprint
import unittest

from .. import config

ConfigReader = config.ConfigReader
PathAction = config.PathAction
read_path_config = config.read_path_config

TestCase = unittest.TestCase


class ConfigReaderTestCase(TestCase):

    """
    Test make_path_action().

    """

    reader = ConfigReader()

    def assertPathAction(self, node, expected):
        actual = self.reader.read_path_action(node)
        self.assertEquals(actual, expected)

    def testReadPathAction(self):
        # Node None.
        self.assertRaises(Exception, self.reader.read_path_action, None)

        self.assertPathAction({}, PathAction(None, False))
        self.assertPathAction({'rename': "foo", "executable": 1}, PathAction("foo", True))

    def testReadPathConfig(self):
        # TODO: create simpler test cases.
        root_node = {
            "rename": "name1",
            "contents": {
                "a": {
                    "contents": {
                        "d": {"rename": "name2"},
                        "c": {"rename": "name3"}
                    }
                },
                "b": {"executable": True}
            }
        }

        path_config = read_path_config(root_node, "root", "dir")
        path_config.sort()

        expected = [
            ('root/dir', PathAction('name1', False)),
            ('root/dir/a/c', PathAction('name3', False)),
            ('root/dir/a/d', PathAction('name2', False)),
            ('root/dir/b', PathAction(None, True))
        ]

        pprint(path_config)
        self.assertEquals(path_config, expected)

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

        # Default arguments.
        self.assertTrue(PathAction(), PathAction(None, None))

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


