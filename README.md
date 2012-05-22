Molt
====

<!-- We leave the brackets empty.  Otherwise, text shows up in the reST
  version converted by pandoc. -->

![](https://github.com/cjerdonek/molt/raw/master/images/molt.png "molting snake")

[Molt](http://cjerdonek.github.com/molt/) is a script to start projects
instantly using [Mustache](http://mustache.github.com/)-based
project templates.

Molt is written in [Python](http://www.python.org/) and follows the
[Groom](http://cjerdonek.github.com/groom/) rules for Mustache-based
project templates.


Requirements
------------

Molt requires Python 2.7.  Python 3.x support is coming soon.  As Molt is a
development tool, there are no plans to support Python 2.6 or earlier.

Molt requires [Pystache](https://github.com/defunkt/pystache) version
[0.5.2](http://pypi.python.org/pypi/pystache).  The install process
below installs Pystache automatically.


Install It
----------

    $ pip install molt


Test it
-------

    $ molt --run-tests


Try it
------

Start with a demo Groom template to play with:

    $ molt --create-demo -o demo
    $ ls demo
    partials	project		sample.json

Render it with the sample context (creating a new project):

    $ molt -o output demo

Run the newly-created project:

    $ python output/hello.py world
    Hello, world!

For help documentation and available options--

    $ molt -h

If using Python, you can also use Molt as a library.  See the `Molter` class
in the [`molt.molter`](https://github.com/cjerdonek/molt/blob/master/molt/molter.py)
module.


Develop
-------

To run unit tests--

    $ python test_molt.py

Which is equivalent to--

    $ python -m molt.commands.molt --run-tests

TODO: add info about submodules.


Features
--------

* Includes a test script that runs all of the molt project tests.
  The test script includes--

  * command-line help,

  * options for verbose and silent output,

  * automatic unit test and doctest discovery,

  * use of Python's [unittest](http://docs.python.org/library/unittest.html)
    and [doctest](http://docs.python.org/library/doctest.html) modules, and

  * integration of doctest with unittest via
    [doctest's unittest API](http://docs.python.org/library/doctest.html#unittest-api).


Examples
--------

This is a temporary example for testing purposes:

    >>> 1 + 1
    2


Author
------

Molt is authored by [Chris Jerdonek](https://github.com/cjerdonek), also
the author of [Groom](http://cjerdonek.github.com/groom/) and the current
[Pystache](https://github.com/defunkt/pystache) maintainer.


Copyright
---------

Copyright (C) 2011-2012 Chris Jerdonek. All rights reserved.

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
