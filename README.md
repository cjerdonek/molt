Molt
====

<!-- We leave the brackets empty.  Otherwise, text shows up in the reST
  version converted by pandoc. -->

![](https://github.com/cjerdonek/molt/raw/master/images/molt.png "molting snake")

[Molt](http://cjerdonek.github.com/molt/) is a script to start projects
instantly using [Mustache](http://mustache.github.com/)-based
project templates.

You can use Molt to decrease the amount of boilerplate code you need to write
when starting any new project: the README, copyright notices, license
info, logging configuration, option parsing, test harness,
packaging information (i.e. setup.py in the case of Python), .gitignore,
directory hierarchy, etc.

A minimal sample usage looks like--

    $ molt -c path_to_config.json path_to_template_dir/

Molt is written in [Python](http://www.python.org/) and follows the
[Groome](http://cjerdonek.github.com/groome/) rules for Mustache-based
project templates.

See the [Groome](http://cjerdonek.github.com/groome/) page for project
template syntax.  This version of Molt follows
[version 0.1.0](https://github.com/cjerdonek/groome/tree/v0.1.0) of Groome.


Requirements
------------

Molt requires Python 2.7.  Python 3.x support is coming soon.  As Molt is a
development tool, there are no plans to support Python 2.6 or earlier.

Molt's dependencies are--

* [Pystache](https://github.com/defunkt/pystache) version
  [0.5.2](http://pypi.python.org/pypi/pystache) or above
* [PyYAML](http://pypi.python.org/pypi/PyYAML) (optional, to support
  YAML format for configuration files)

TODO: include setup dependencies

The installation process below installs these dependencies automatically.


Install It
----------

    $ pip install molt


Test it
-------

    $ molt --run-tests


Try it
------

Start with the [demo](https://github.com/cjerdonek/molt/tree/master/molt/demo)
Groome template to play with:

    $ molt --create-demo --output demo
    $ ls -p demo
    lambdas/    partials/    project/    sample.json

Render the template with the sample context provided:

    $ molt --output output --config demo/sample.json demo

Run the newly-created project (which can also be seen
[here](https://github.com/cjerdonek/molt/tree/master/molt/test/data/demo)):

TODO: do I need to correct the next line?

    $ molt output/hello.py world
    Hello, world!

For help documentation and available options--

    $ molt -h

Note the `--visualize` and `--with-visualize` options that let you
quickly visualize entire directory contents.

    $ molt --visualize output

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

To include the Groome [tests](https://github.com/cjerdonek/groome/tree/master/tests)
in your test runs, initialize and update the Groome project submodule--

    $ git submodule init
    $ git submodule update

To run a subset of the tests, you can filter your test runs using one or
more prefixes.  For example--

    $ python test_molt.py molt.test.common molt.test.dir


Author
------

Molt is authored by [Chris Jerdonek](https://github.com/cjerdonek).
Chris is also the author of [Groome](http://cjerdonek.github.com/groome/) and
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
