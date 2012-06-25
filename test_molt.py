# encoding: utf-8

"""
Runs project tests.

This script is a convenience wrapper for running--

    python -m molt.commands.molt --run-tests [plus more options]

"""

import os
import sys

from molt.commandline import OPTION_MODE_TESTS, OPTION_SOURCE_DIR
from molt.commands import molt


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # TODO: consider passing the extra info via **kwargs instead of sys_argv.
    source_dir = os.path.dirname(__file__)
    argv += [OPTION_MODE_TESTS[0], OPTION_SOURCE_DIR[0], source_dir]

    return molt.main(sys_argv=argv)


if __name__ == "__main__":
    result = main()
    sys.exit(result)
