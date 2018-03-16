skt - sonic kernel testing
==========================

Skt is a tool for automatically fetching, building, and testing kernel
patches published on Patchwork instances.

Dependencies
------------

Install dependencies needed for running skt like this:

    $ sudo dnf install python2 python2-junit_xml beaker-client

Dependencies needed to build kernels:

    $ sudo dnf builddep kernel-`uname -r`
    $ sudo dnf install bison flex

Extra dependencies needed for running the testsuite:

    $ sudo dnf install python2-mock

Run tests
---------

For running all tests write down:

    $ python -m unittest discover tests

For running some specific tests you can do this as following:

    $ python -m unittest tests.test_publisher

License
-------
skt is distributed under GPLv2 license.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
