TODO
====

Do next:

* README documentation for Python 3.

Others:

* Add some test cases with non-latin1 filename encodings.
* In setup.py, scrape the version number from the package `__init__.py`.
* Rename project to structure inside molter.py and dirutil.
* Confirm whether setup.py's publishing can only be done with Python 2.x.
* Add the ability to "check" a template directory from the command-line.
* Add a unit test for --verbose working with unit tests.
* Add an --overwrite option to write over (but not delete) existing output
  directories.
* Add a --strict-output-dir mode that causes the program to fail if
  the output directory already exists.
* Add an option to enable stdout for tests.
* Consider switching from optparse to argparse.
* Incorporate this advice:
    http://mail.python.org/pipermail/distutils-sig/2009-November/014370.html
* Add an exception class that you can add messages to.
* Make the script Unicode aware using the guidance [here](http://docs.python.org/howto/unicode.html).
* Separate tester code from tester config, and put the tester code into
  a subfolder.
* Consider running pylint, PyChecker, and/or pep8 in addition to the
  doctests in each module.
* [move to groome-python].  Add git files.
