# coding: utf-8

"""
This module provides a command to test pystache (unit tests, doctests, etc).

"""

from __future__ import absolute_import

import sys

from molt.main import run


def main(sys_argv=sys.argv):
    return run(sys_argv=sys_argv)


if __name__ == "__main__":
    result = main()
    sys.exit(result)
