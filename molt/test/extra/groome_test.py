# encoding: utf-8
#
# Copyright (C) 2011-2012 Chris Jerdonek. All rights reserved.
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
Exposes tests that test the Groome project test cases.

"""

import logging
import os
import unittest

from molt.test.harness import config_load_tests, test_logger as _log
from molt.test.harness.templatetest import make_template_tests_class


def load_tests(loader, tests, pattern):
    """
    Return a unittest.TestSuite instance of all Groome project tests.

    Arguments:

      tests: a unittest.TestSuite instance of the standard tests loaded
        from this module.

    """
    groome_dir = loader.test_config.groome_tests_dir

    template_tests = unittest.TestSuite()

    if groome_dir is None:
        # Then Groome tests are not expected to be available.
        pass
    elif not os.path.exists(groome_dir):
        _log.warn("Groome tests directory not found: %s\n"
                  "  Consult the documentation on how to include them." % groome_dir)
    else:
       type_args = make_template_tests_class(group_name='Groome',
                                             parent_input_dir=groome_dir)
       # We define the class in this module so that the test harness reports
       # the TestCase class as originating from this module.
       test_class = type(*type_args)
       template_tests = loader.loadTestsFromTestCase(test_class)

    _log.info("found %s Groome tests in dir: %s" % (template_tests.countTestCases(), groome_dir))

    tests.addTests(template_tests)

    tests = config_load_tests(loader, tests, pattern)

    return tests
