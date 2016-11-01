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

.. describe:: entry_point

   The function to launch your application, in the format ``module:function``.
   Dots are allowed in the module part. pynsist will create a script like this,
   plus some boilerplate::

       from module import function
       function()

.. describe:: script (optional)

   Path to the Python script which launches your application, as an alternative
   to ``entry_point``.

   Ensure that this boilerplate code is at the top of your script::

       #!python3.3
       import sys
       sys.path.insert(0, 'pkgs')

   The first line tells it which version of Python to run with. If you use
   binary packages, packages compiled for Python 3.3 won't work with Python 3.4.
   The other lines make sure it can find the packages installed along with your
   application.

.. describe:: target (optional)
              parameters (optional)

   Lower level definition of a shortcut, to create start menu entries for help
   pages or other non-Python entry points. You shouldn't normally use this for
   Python entry points.

.. note::
   Either ``entry_point``, ``script`` or ``target`` must be specified, but not
   more than one. Specifying ``entry_point`` is normally easiest and most
   reliable.

.. describe:: icon (optional)

  Path to a ``.ico`` file to be used for shortcuts to your application. Pynsist
  has a default generic icon, but you probably want to replace it.

.. describe:: console (optional)

   If ``true``, shortcuts will be created using the ``py`` launcher, which opens
   a console for the process. If ``false``, or not specified, they will use the
   ``pyw`` launcher, which doesn't create a console.

.. describe:: extra_preamble (optional)

   Path to a file containing extra Python commands to be run before your code is
   launched, for example  to set environment variables needed by pygtk. This is
   only valid if you use ``entry_point`` to specify how to launch your application.
   
   If you use the Python API, this parameter can also be passed as a file-like
   object, such as :class:`io.StringIO`.

.. _shortcut_config:

Shortcut sections
-----------------

One shortcut will always be generated for the application. You can add extra
shortcuts by defining sections titled :samp:`Shortcut {Name}`. For example:

.. code-block:: ini

    [Shortcut IPython Notebook]
    entry_point=IPython.html.notebookapp:launch_new_instance
    icon=scripts/ipython_nb.ico
    console=true

.. describe:: entry_point
              script (optional)
              icon (optional)
              console (optional)
              target (optional)
              parameters (optional)
              extra_preamble (optional)

   These options all work the same way as in the Application section.


.. _command_config:

Command sections
----------------

.. versionadded:: 1.7

Your application can install commands to be run from the Windows command prompt.
This is not standard practice for desktop applications on Windows, but if your
application specifically provides a command line interface, you can define
one or more sections titled :samp:`Command {name}`::

    [Command guessnumber]
    entry_point=guessnumber:main

If you use this, the installer will modify the system :envvar:`PATH` environment
variable.

.. describe:: entry_point

   As with shortcuts, this specifies the Python function to call, in the format
   ``module:function``.

.. describe:: extra_preamble (optional)

   As for shortcuts, a file containing extra code to run before importing the
   module from ``entry_point``. This should rarely be needed.

.. _cfg_python:

Python section
--------------

.. describe:: version

  The Python version to download and bundle with your application, e.g. ``3.4.3``.
  Python 3.3 or later and 2.7 are supported.

.. describe:: bitness (optional)

  ``32`` or ``64``, to use 32-bit (x86) or 64-bit (x64) Python. On Windows, this
  defaults to the version you're using, so that compiled modules will match. On
  other platforms, it defaults to 32-bit.

.. describe:: format (optional)

  - ``installer`` includes a copy of the Python MSI installer in your application
    and runs it at install time, setting up Python systemwide. This is the
    default for Python up to 3.5.
  - ``bundled`` includes an embeddable Python build, which will be installed as
    part of your application. This is available for Python 3.5 and above, and is
    the default for Python 3.6 and above.

  .. versionchanged:: 1.9

     The default switched to ``bundled`` for Python 3.6 and above.

.. describe:: include_msvcrt (optional)

  This option is only relevant with ``format = bundled``. The default is ``true``,
  which will include an app-local copy of the Microsoft Visual C++ Runtime,
  required for Python to run. The installer will only install this if it doesn't
  detect a system installation of the runtime.

  Setting this to ``false`` will not include the C++ Runtime. Your application may
  not run for all users until they install it manually (`download from Microsoft
  <https://www.microsoft.com/en-us/download/details.aspx?id=48145>`__). You may
  prefer to do this for security reasons: the separately installed runtime will
  get updates through Windows Update, but app-local copies will not.

  Users on Windows 10 should already have the runtime installed systemwide, so
  this does won't affect them. Users on Windows Vista, 7, 8 or 8.1 *may* already
  have it, depending on what else is installed.

  .. versionadded:: 1.9

.. _python_bundled:

Bundled Python
~~~~~~~~~~~~~~

.. versionadded:: 1.6
   Support for bundling Python into the application.

Using ``format = bundled``, an embeddable Python build will be downloaded at
build time and packaged along with the application. When the installer runs, it
will create a ``Python`` subfolder inside the install directory with the files
Python needs to run.

This has the advantage of producing smaller, quicker installers (~7.5 MB for a
trivial application), and more standalone installations. But it has a number of
limitations:

- This option is only available for Python 3.5 and above. These versions of
  Python have dropped support for Windows XP, so your application will only work
  on Windows Vista and newer.
- Installing in Windows Vista to 8.1 (inclusive) may install an app-local copy
  of the Visual C++ runtime (see above). This isn't
  needed on Windows 10, which includes the necessary files.
- The embeddable Python builds don't include ``tkinter``, to save space.
  Applications with a tkinter GUI can't easily use bundled Python. Workarounds
  may be found in the future.
- The user cannot easily install extra Python packages in the application's
  Python. If your application has plugins based on Python packages, this might
  require extra thought about how and where plugins are installed.

Include section
---------------

To write these lists, put each value on a new line, with more indentation than
the line with the key:

.. code-block:: ini

    key=value1
      value2
      value3

.. describe:: packages (optional)

   A list of importable package and module names to include in the installer.
   Specify only top-level packages, i.e. without a ``.`` in the name.

.. describe:: pypi_wheels (optional)

   A list of packages to download from PyPI, in the format ``name==version``.
   These must be available as wheels; Pynsist will not try to download sdists
   or eggs.

   .. versionadded:: 1.7

.. describe:: files (optional)

   Extra files or directories to be installed with your application.

   You can optionally add ``> destination`` after each file to install it
   somewhere other than the installation directory. The destination can be:

   * An absolute path on the target system, e.g. ``C:\\`` (but this is not
     usually desirable).
   * A path starting with ``$INSTDIR``, the specified installation directory.
   * A path starting with any of the `constants NSIS provides
     <http://nsis.sourceforge.net/Docs/Chapter4.html#4.2.3>`_, e.g. ``$SYSDIR``.

   The destination can also include ``${PRODUCT_NAME}``, which will be expanded
   to the name of your application.

   For instance, to put a data file in the (32 bit) common files directory:

   .. code-block:: ini

       [Include]
       files=mydata.dat > $COMMONFILES

.. describe:: exclude (optional)

   Files to be excluded from your installer. This can be used to include a
   Python library or extra directory only partially, for example to include
   large monolithic python packages without their samples and test suites to
   achieve a smaller installer file.

   Please note:

   * The parameter is expected to contain a list of files *relative to the
     build directory*. Therefore, to include files from a package, you have to
     start your pattern with ``pkgs/<packagename>/``.
   * You can use `wildcard characters`_ like ``*`` or ``?``, similar to a Unix 
     shell.
   * If you want to exclude whole subfolders, do *not* put a path separator 
     (e.g. ``/``) at their end.
   * The exclude patterns are only applied to packages and to directories
     specified using the ``files`` option. If your ``exclude`` option directly 
     contradicts your ``files`` or ``packages`` option, the files in question
     will be included (you can not exclude a full package/extra directory
     or a single file listed in ``files``).

   Example:

   .. code-block:: ini

       [Include]
       packages=PySide
       files=data_dir
       exclude=pkgs/PySide/examples
         data_dir/ignoredfile

Build section
-------------

.. describe:: directory (optional)

   The build directory. Defaults to ``build/nsis/``.

.. describe:: installer_name (optional)

   The filename of the installer, relative to the build directory. The default
   is made from your application name and version.

.. describe:: nsi_template (optional)

   The path of a template .nsi file to specify further details of the installer.
   The default template is `part of pynsist <https://github.com/takluyver/pynsist/blob/master/nsist/pyapp.nsi>`_.

   This is an advanced option, and if you specify a custom template, you may
   well have to update it to work with future releases of Pynsist.

   See the `NSIS Scripting Reference <http://nsis.sourceforge.net/Docs/Chapter4.html>`_
   for details of the NSIS language, and the Jinja2 `Template Designer Docs
   <http://jinja.pocoo.org/docs/dev/templates/>`_ for details of the template
   format. Pynsist uses templates with square brackets (``[]``) instead of
   Jinja's default curly braces (``{}``).

.. _wildcard characters: https://docs.python.org/3/library/fnmatch.html
