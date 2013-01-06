# encoding: utf-8

"""
Runs project tests.

This script is a convenience wrapper for running--

    python -m molt.commands.molt --run-tests [plus more options]

"""

import os
import sys

from molt.argparsing import OPTION_MODE_TESTS, OPTION_SOURCE_DIR
from molt.commands.molt import main as main_module


# TODO: change this script from running tests to calling molt.commands.molt
# with the right from-source options.  That way this convenience script
# can be used for more than just running tests.
def main(argv=None):
    if argv is None:
        argv = sys.argv

    # TODO: consider passing the extra info via **kwargs instead of sys_argv.
    source_dir = os.path.dirname(__file__)

    # Modify argv in place.
    #
    # Insert the test option after the program name but before all other
    # arguments.  In this way, test filters should always appear at the
    # beginning of the argument list in this form of invoking the
    # script in test mode.
    argv.insert(1, OPTION_MODE_TESTS[0])

    # Since this script exists in the source folder but not in the
    # package folder, it can only be run in the presence of source.
    # Pass the source information along to indicate this..
    argv += [OPTION_SOURCE_DIR[0], source_dir]

    main_module.main(sys_argv=argv, from_source=True)


if __name__ == "__main__":
    main()
