The Config File
===============

All paths in the config file are relative to the directory where the config
file is located, unless noted otherwise.

Application section
-------------------

.. describe:: name

  The user-readable name of your application. This will be used for various
  display purposes in the installer, and for shortcuts and the folder in
  'Program Files'.

.. describe:: version

  The version number of your application.

.. describe:: script

  Path to the Python script which launches your application.

.. describe:: icon (optional)

  Path to a ``.ico`` file to be used for shortcuts to your application. pynsis
  has a default generic icon, but you probably want to replace it.

.. describe:: console (optional)

   If ``true``, shortcuts will be created using the ``py`` launcher, which opens
   a console for the process. If ``false``, or not specified, they will use the
   ``pyw`` launcher, which doesn't create a console.

.. _cfg_python:

Python section
--------------

.. describe:: version

  The Python version to download and bundle with your application. At present,
  this needs to be at least ``3.3.0``.

.. describe:: bitness (optional)

  ``32`` or ``64``, to use 32-bit (x86) or 64-bit (x64) Python. On Windows, this
  defaults to the version you're using, so that compiled modules will match. On
  other platforms, it defaults to 32-bit.

Include section
---------------

.. describe:: packages (optional)

   A list of importable package and module names to include in the installer.
   Specify only top-level packages, i.e. without a ``.`` in the name.

.. describe:: files (optional)

   Extra files to be installed with your application.

Build section
-------------

.. describe:: directory (optional)

   The build directory. Defaults to ``build/nsis/``.

.. describe:: installer_name (optional)

   The filename of the installer, relative to the build directory. The default
   is made from your application name and version.
