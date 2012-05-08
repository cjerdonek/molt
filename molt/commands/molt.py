# coding: utf-8

"""
Provides the setup() entry point for the main molt command-line script.

"""

from __future__ import absolute_import

import sys

from molt.main import run


def main(sys_argv=sys.argv):
    return run(sys_argv=sys_argv)


if __name__ == "__main__":
    result = main()
    sys.exit(result)
