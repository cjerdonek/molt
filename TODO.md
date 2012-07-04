TODO
====

* Refactor AssertFileMixin to use a new fuzzy file-matching function
  that we can add to molt.diff.
* Create a pure-Python diff() function and switch the unit tests to use it.
* Add the ability to "check" a template directory from the command-line.
* Rename project to structure inside molter.py and dirutil.
* Review all appearances of `__file__` (using projectmap as necessary).

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
