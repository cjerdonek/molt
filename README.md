Molt
====

<!-- We leave the brackets empty.  Otherwise, text shows up in the reST
  version converted by pandoc. -->

![](https://github.com/cjerdonek/molt/raw/master/images/molt.png "molting snake")

[Molt](http://cjerdonek.github.com/molt/) is a script to start projects
instantly using [Mustache](http://mustache.github.com/)-based
project templates.

You can use Molt to decrease the amount of boiler-plate code you need to write
when starting any new project: the README, copyright notices, license
info, logging configuration, test harness, packaging information (i.e.
setup.py in the case of Python), .gitignore, directory hierarchy, etc.

Molt is written in [Python](http://www.python.org/) and follows the
[Groom](http://cjerdonek.github.com/groom/) rules for Mustache-based
project templates.  See the Groom page for project template syntax.


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

Start with the [demo](https://github.com/cjerdonek/molt/tree/master/molt/demo)
Groom template to play with:

    $ molt --create-demo --output demo
    $ ls -p demo
    lambdas/    partials/    project/    sample.json

Render the template with the sample context provided:

    $ molt --output output --config demo/sample.json demo

Run the newly-created project (which can also be seen
[here](https://github.com/cjerdonek/molt/tree/master/molt/test/data/demo)):

    $ python output/hello.py world
    Hello, world!

For help documentation and available options--

    $ molt -h

If using Python, you can also use Molt as a library (though the API is
not yet stable).  See the `Molter` class in the
[`molt.molter`](https://github.com/cjerdonek/molt/blob/master/molt/molter.py)
module.


Contribute
----------

If using [GitHub](https://github.com/), after forking--

    $ git clone git@github.com:yourusername/molt.git
    $ cd molt
    $ git remote add upstream git://github.com/cjerdonek/molt.git
    $ git fetch upstream

To run unit tests--

    $ python test_molt.py

This is equivalent to--

    $ python -m molt.commands.molt --run-tests

In particular, to test from source any molt command (of the form)--

    $ molt [options] [DIRECTORY]

simply type--

    $ python -m molt.commands.molt [options] [DIRECTORY]

To include the Groom [tests](https://github.com/cjerdonek/groom/tree/master/tests)
in your test runs, initialize and update the Groom project submodule--

    $ git submodule init
    $ git submodule update


Author
------

Molt is authored by [Chris Jerdonek](https://github.com/cjerdonek).
Chris is also the author of [Groom](http://cjerdonek.github.com/groom/) and
is the current [Pystache](https://github.com/defunkt/pystache) maintainer.


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
