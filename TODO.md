TODO
====

Before releasing version 0.1.0:

 * finalize README.
 * finalize help options and help strings.
 * stub out history file
 * make setup.py file
 * support Python 2.7.
 * demo should illustrate all syntactic aspects.
 * make an "end-to-end" test using os.system.
 * Generate a GitHub page just before the release to PyPI.
 * Mention the API on the README.

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
* [move to groom-python] Add git files.
