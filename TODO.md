TODO
====

Milestones
----------

1. Get to where I can improve a Groome template using an efficient workflow.
2. Have Molt be based on a Groome template, and vice versa.

Steps
-----

* Remove references to optparse (case-sensitive) and OptionParser.
* Correct parser return value docstring.
* Add PEP 8 linter support to the setup package.
  Does this make sense?
* Double-check that molt_setup can be left out of setup()'s packages
  but still be installed via pip, etc.
* Create file and directory comparing functions and switch the unit tests
  to using them.
* Add the ability to "check" a template directory from the command-line.
* Rename project to structure inside molter.py and dirutil.

* Review all appearances of `__file__` (using projectmap as necessary).
* Review all appearances of 'utf-8'.
* Add some test cases with non-latin1 filename encodings.
* Confirm whether setup.py's publishing can only be done with Python 2.x.
* Add a unit test for --verbose working with unit tests.
* Add an --overwrite option to write over (but not delete) existing output
  directories.
* Add a --strict-output-dir mode that causes the program to fail if
  the output directory already exists.
* Add an option to enable stdout for tests.
* Incorporate this advice:
    http://mail.python.org/pipermail/distutils-sig/2009-November/014370.html
* Add an exception class that you can add messages to.
* Make the script Unicode aware using the guidance [here](http://docs.python.org/howto/unicode.html).
* Separate tester code from tester config, and put the tester code into
  a subfolder.
* Consider running pylint, PyChecker, and/or pep8 in addition to the
  doctests in each module.
* [move to groome-python].  Add git files.
