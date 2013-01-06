# encoding: utf-8

"""
Runs project tests.

This script is a convenience wrapper for running the following while
developing:

    python -m molt.scripts.molt

"""

import os
import sys

from molt.scripts.molt import argparsing
from molt.scripts.molt import main as main_module


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # TODO: consider passing the extra info via **kwargs instead of sys_argv.
    source_dir = os.path.dirname(__file__)

    # TODO: do we need to insert this at the beginning rather than at the end?
    # Since this script exists in the source folder but not in the
    # package folder, it can only be run in the presence of source.
    # Pass the source information along to indicate this..
    argv += [argparsing.OPTION_SOURCE_DIR[0], source_dir]

    main_module.main(sys_argv=argv, from_source=True)


if __name__ == "__main__":
    main()
