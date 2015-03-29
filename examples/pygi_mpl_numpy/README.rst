This example shows how to package a program that uses the PyGI-bindings of Gtk (or PyGObject). Python 3.4.3 64-bit will be used together with 64-bit dependencies.

The example program conists of a window with a matplotlib-plot and a button that triggers the window to close.

Requirements
------------

This example needs 7zip in order to work. You can install it for example on
Debian-style distributions using:

::

    sudo apt-get install p7zip

Building the program
--------------------

A shell script can be used to download some of the dependencies:

::

    sh 1_download.sh

The numpy 64-bit wheel can be downloaded here (numpy‑1.9.2+mkl‑cp34‑none‑win_amd64.whl):

http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

Rename it to numpy.whl before starting the second script.

The next script will copy all the dependencies into the ``pynsist_pkgs`` folder.

::

    sh 2_extract.sh

After that, the example can be built using this command:

::

    python3 -m nsist installer.cfg

Installer.cfg
-------------

The example uses 64-bit Python 3.4 and 64-bit dependencies. This is expressed in the
``installer.cfg``-file like this:

::

    version=3.4.3
    bitness=64

The include section requires the Python packages numpy, matplotlib (which are taken from the ``pynsist_pkgs`` folder). In addition the packages six, dateutil and pyparsing are required. From the pygi-bindings the top level packages cairo, dbus, gi, gnome and pygtkcompat have to be listed here (They are also in the top level of the ``pynsist_pkgs`` directory). The ``gnome``-folder contains the dependencies ATK, Base, GDK, GDKPixbuf, GTK, JPEG, Pango, WebP and TIFF.

::

    [Include]
    packages=gi
        cairo
        dbus
        gnome
        pygtkcompat
        numpy
        matplotlib
        six
        dateutil
        pyparsing

