**This example does not currently work**: Pynsist 2 requires Python 3.5 or above,
but PyGI is only available for Python 3.4 at most (as of October 2017).
Hopefully it will be possible again in the future.

This example shows how to package a program that uses the PyGI-bindings of Gtk (or PyGObject).
Python 3.4.3 64-bit will be used together with 64-bit dependencies.

The example program consists of a window with a matplotlib-plot and a button that triggers the window to close.

Requirements
------------

This example needs 7zip in order to work. You can install it for example on
Debian-style distributions using:

::

    sudo apt-get install p7zip

Building the program
--------------------

A shell script can be used to download the PyGI Windows installer:

::

    sh 1_download.sh

The next script will extract the necessary GTK components into the
``pynsist_pkgs`` folder.

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

glib-schemas
------------

When the pygi-aio bundle is installed on a Windows-machine, the installer performs some post-installation compiling steps. After extracting the libraries from the bundle, compiling can be carried out on Linux, as long as the operating system used for packaging and the targeted operating system have the same bitness. For different bitnesses, use a virtual machine with desired bitness, install the bundle, and copy the compiled files back into your build directory.

An example are the glib-schemas which are required for the GtkFileChooserDialog to work properly. The script ``2_extract.sh`` will automatically call the following command to compile the glib-schemas:

::

    glib-compile-schemas pynsist_pkgs/gnome/share/glib-2.0/schemas/

Note: If your application uses glib-schemas (e.g. default-settings stored in gsettings) you will need to place the schemas for your application into that folder and recompile it before packaging it with Pynsist.

See also:

 - https://github.com/takluyver/pynsist/issues/43
 - https://sourceforge.net/p/pygobjectwin32/tickets/12/
