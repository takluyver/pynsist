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

.. versionadded:: 0.2

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

To write these lists, put each value on a new line, with more indentation than
the line with the key:

.. code-block:: ini

    key=value1
      value2
      value3

.. describe:: packages (optional)

   A list of importable package and module names to include in the installer.
   Specify only top-level packages, i.e. without a ``.`` in the name.

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
