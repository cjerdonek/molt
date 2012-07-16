Molt
====

<!-- We strip out 1-line HTML comments prior to passing to pandoc because -->
<!-- PyPI rejects reST long descriptions that contain HTML. -->

<!-- We leave the leading brackets empty here.  Otherwise, unwanted -->
<!-- caption text shows up in the reST version converted by pandoc. -->
![](https://github.com/cjerdonek/molt/raw/master/images/molt.png "molting snake")

![](https://secure.travis-ci.org/cjerdonek/molt.png?branch=master,development)

[Molt](http://cjerdonek.github.com/molt/) is a script to stub out projects
in any language instantly using [Mustache](http://mustache.github.com/)-based
project templates.

You can use Molt to decrease the amount of boilerplate code you need to write
when starting new projects: the README, copyright notices, license info,
logging configuration, option parsing, test harness, packaging information,
`.gitignore`, directory hierarchy, etc.

A minimal sample usage looks like--

    $ molt -c path_to_config.json path_to_template_dir/

Molt follows the [Groome](http://cjerdonek.github.com/groome/) rules for
Mustache-based project templates.
See the [Groome](http://cjerdonek.github.com/groome/) page for project
template syntax.  This version of Molt follows
[version 0.1.0](https://github.com/cjerdonek/groome/tree/v0.1.0) of Groome.

Molt is written in [Python](http://www.python.org/) and can be found on
[GitHub](https://github.com/cjerdonek/molt) and on
[PyPI](http://pypi.python.org/pypi/molt) (the Python Package Index).

Feedback is welcome.  You can also file bug reports and feature requests
on the GitHub [issues page](https://github.com/cjerdonek/molt/issues).


Requirements
------------

Molt supports the following Python versions:

* Python 2.7
* Python 3.2
* [PyPy](http://pypy.org/)

Since Molt is a development tool, there are no plans to support Python 2.6
or earlier.

Molt's dependencies are--

* [Pystache](https://github.com/defunkt/pystache) version
  [0.5.2](http://pypi.python.org/pypi/pystache) or above
* [PyYAML](http://pypi.python.org/pypi/PyYAML) (optional, to support
  YAML format for configuration files)

The installation process below installs these dependencies automatically.

You can install to Python 2 with either
[setuptools](http://pypi.python.org/pypi/setuptools) or
[Distribute](http://packages.python.org/distribute/) (preferred).
For Python 3, you must use Distribute.


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
    expected/	lambdas/	partials/	sample.json	structure/

Render the template with the sample context provided:

    $ molt --output output --config demo/sample.json demo

Run the newly-created project (which can also be seen
[here](https://github.com/cjerdonek/molt/tree/master/molt/demo/expected))):

    $ python output/hello.py world
    Hello, world!

For help documentation and available options--

    $ molt -h

Note the `--visualize` and `--with-visualize` options that let you
quickly visualize entire directory contents.

    $ molt --visualize output

If using Python, you can also use Molt as a library (though the API is
not yet stable).  See the `Molter` class in the
[molt.molter](https://github.com/cjerdonek/molt/blob/master/molt/molter.py)
module.


Contribute
----------

If using GitHub, after forking--

    $ git clone git@github.com:yourusername/molt.git
    $ cd molt
    $ git remote add upstream git://github.com/cjerdonek/molt.git
    $ git fetch upstream

To run unit tests--

    $ python test_molt.py

To test Molt with multiple versions of Python (with a single command!),
you can use [tox](http://tox.testrun.org/):

    pip install tox
    tox

If you don't have all Python versions listed in `tox.ini`, you can do--

    tox -e py27  # for example

To run from source any molt command of the form--

    $ molt [options] [DIRECTORY]

simply type--

    $ python -m molt.commands.molt [options] [DIRECTORY]

To include the [Groome tests](https://github.com/cjerdonek/groome/tree/master/tests)
in your test runs, initialize and update the Groome project submodule--

    $ git submodule init
    $ git submodule update

To run a subset of the tests, you can filter your test runs using one or
more prefixes.  For example--

    $ python test_molt.py molt.test.general molt.test.dir

Molt is also [set up](https://github.com/cjerdonek/molt/blob/master/.travis.yml)
on GitHub to work with [Travis CI](http://travis-ci.org/).


### Python 3 Tips

Molt is written in Python 2, so the code must be converted to Python 3 prior
to using with Python 3.  The installation process does this automatically.

To convert the code to Python 3 manually, run the following using Python 3
(with Distribute installed)--

    python setup.py build

This writes the converted code to a subdirectory of the project directory
called `build`.

It is possible (though not recommended) to convert the code without using
`setup.py`.  You can try this with [2to3](http://docs.python.org/library/2to3.html),
as follows (two steps):

    2to3 --write --nobackups --no-diffs --doctests_only molt
    2to3 --write --nobackups --no-diffs molt

This converts the code (and doctests) in place.

To `import molt` from a source distribution while using Python 3, be sure
that you are importing from a directory containing the converted code
(e.g. from the `build` directory after converting), and not from the
original (unconverted) source directory.  Otherwise, you will get a
syntax error.  You can help prevent this by not running the Python
IDE from the project directory when importing Molt while using Python 3.


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
