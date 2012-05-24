TODO
====

Before releasing version 0.1.0:

 * refactor and clean up code and logic around partials and lambdas directory.
 * finalize README.
 * make the demo like Groom's "Advanced Example".
 * finalize help options and help strings.
 * make setup.py file
 * make an "end-to-end" test using subprocess.
 * Make sure HISTORY file, etc. is included in the MANIFEST.

* Make log messages begin with a newline on some condition.
* Add an --overwrite option to write over (but not delete) existing output
  directories.
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
* Support YAML configuration files.
