# encoding: utf-8

"""
Runs project tests.

This script is a convenience wrapper for running--

    python -m molt.commands.molt --run-tests

"""

import sys

from molt.commandline import OPTION_MODE_TESTS
from molt.commands import molt


def main(argv=None):
    if argv is None:
        # Make a copy since we will modify it.
        argv = list(sys.argv)

    argv.insert(1, OPTION_MODE_TESTS[0])
    return molt.main(sys_argv=argv)


if __name__ == "__main__":
    result = main()
    sys.exit(result)
