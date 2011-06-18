molt (Python Project Creator)
=============================

molt is a Python script for starting new Python projects without all the
drudgery.  The resulting project uses good practices and includes
plumbing and stubs for documentation, unit tests,
[doctests](http://docs.python.org/library/doctest.html), logging, etc.
It is driven by [YAML](http://www.yaml.org/) configuration files and
propelled under the hood by [mustache](http://mustache.github.com/) templates.


Features
--------

* Tested with Python 2.6 and 2.7.

* Includes a test script that runs all unit tests and doctests in the project.
  The test script includes--
  
  * command-line help,
  
  * options for verbose and silent output,

  * automatic unit test and doctest discovery,

  * use of Python's [unittest](http://docs.python.org/library/unittest.html)
    and [doctest](http://docs.python.org/library/doctest.html) modules, and

  * [integration of doctest with unittest](http://docs.python.org/library/doctest.html#unittest-api)
    via the unittest API.


Project Contents
----------------

    molt . . . . . . . . . the main script.
    molt_lib/  . . . . . . supporting code for the main molt script.
    test_molt  . . . . . . script to run all project tests.
    tester_lib/  . . . . . supporting code for the test_molt script.


Examples
--------

This is a temporary test of a doctest failure:

    >>> 1 + 1
    3


TODO
----

The script is still in progress and not yet usable.  Comments and
suggestions are welcome.

Chris Jerdonek


Copyright
---------

Copyright (C) 2011 Chris Jerdonek. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* The names of the copyright holders may not be used to endorse or promote
  products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
