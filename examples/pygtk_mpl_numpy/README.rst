This is an example of building a Windows installer for a pygtk application that
includes matplotlib and numpy.

Requirements
------------

This example needs 7zip in order to work. You can install it for example on
Debian-style distributions using:

::

    sudo apt-get install p7zip

Running the Example
-------------------

In order to build the example application on Linux you have to run the following
two commands in the example directory:

::

    sh grab_files.sh
    python -m nsist installer.cfg

The first line will download the dependencies, extract them and copy them into
the :code:`pynsist_pkgs`-directory. It will then remove the temporary directories
used for extraction, but will leave the downloaded archives intact in the
example directory.

Matplotlib
----------

The example downloads the 32-bit Python 2.7 bindings of Matplotlib 1.4.3
(matplotlib-1.4.3.win32-py2.7.exe).

In the :code:`installer.cfg` Matplotlib additionally requires the six, dateutil
and pyparsing packages:

::

    [Include]
    packages=pygtk
        numpy
        matplotlib
        six
        dateutil
        pyparsing

Numpy
-----

The example downloads the 32-bit Python 2.7 bindings of Numpy 1.9.2
(numpy-1.9.2-win32-superpack-python2.7.exe).

PyGTK
-----

PyGTK is a bit more complex than the other examples, because the GTK runtime
needs to be set up. This needs two things:

1. The pieces of the GTK runtime and its Python bindings. The script ``grab_files.sh``
   downloads these, unpacks them, trims out unnecessary pieces, and places them
   where pynsist will find them.
2. The ``PATH`` environment variable must be modified before we try to import
   the Python GTK bindings. This is done by the ``extra_preamble`` field in
   ``installer.cfg``.

I referred to the following sources of information to work this out:

Bundling pygtk using py2exe:
http://faq.pygtk.org/index.py?file=faq21.005.htp&req=show
https://web.archive.org/web/20060208162511/http://www.anti-particle.com/py2exe-0.5.shtml

Installing pygtk & deps: http://www.pygtk.org/downloads.html
(inc links for pygtk, pycairo and pygobject installers)

GTK bundles for Windows: http://www.gtk.org/download/win32.php

Installer.cfg
-------------

The example is customized for 32-bit and Python 2.7. This is expressed in the
:code:`installer.cfg`-file like this:

::

    version=2.7.9
    bitness=32

The include section requires pygtk, numpy and matplotlib. In order to satisfy the
requirements of Matplotlib the packages six, dateutil, and pyparsing are needed.

::

    [Include]
    packages=pygtk
        numpy
        matplotlib
        six
        dateutil
        pyparsing
