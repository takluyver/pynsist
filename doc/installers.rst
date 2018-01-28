Installer details
=================

The installers pynsist builds do a number of things:

1. Install a number of files in the installation directory the user selects:

   - An embedded build of Python, including the standard library.
   - A copy of the necessary Microsoft C runtime for Python to run, if this
     is not already installed on the system.
   - The launcher script(s) that start your application
   - The icon(s) for your application launchers
   - Python packages your application needs
   - Any other files you specified

2. Create a start menu shortcut for each launcher script. If there is only one
   launcher, it will go in the top level of the start menu. If there's more than
   one, the installer will make a folder named after the application.
3. If you have specified any :ref:`commands <command_config>`, modify the
   :envvar:`PATH` environment variable in the registry, so that your commands
   will be available in a system command prompt.
4. Byte-compile all Python files in the ``pkgs`` subdirectory. This should
   slightly improve the startup time of your application.
5. Write an uninstaller, and the registry keys to put it in 'Add/remove programs'.

The installer (and uninstaller) is produced using `NSIS
<http://nsis.sourceforge.net/Main_Page>`_, with the Modern UI.

Uncaught exceptions
-------------------

If there is an uncaught exception in your application - for instance if it fails
to start because a package is missing - the traceback will be written to
:file:`%APPDATA%\\{scriptname}.log`. On Windows 7, :envvar:`APPDATA` defaults to
:file:`C:\\Users\\{username}\\AppData\\Roaming`. If users report crashes, details
of the problem will probably be found there.

You can override this by setting :func:`sys.excepthook`.

This is only provided if you specify your application using ``entry_point``.

You can also debug an installed application by using the installed Python to
launch the application. This will show tracebacks in the Command Prompt.
In the installation directory run::

       C:\\Program Files\\Application>Python\\python.exe "Application.launch.pyw"

Working directory
-----------------

If users start your application from the start menu shortcuts, the working
directory will be set to their home directory (``%HOMEDRIVE%%HOMEPATH%``). If
they double-click on the scripts in the installation directory, the working
directory will be the installation directory. Your application shouldn't
rely on having a particular working directory; if it does, use :func:`os.chdir`
to set it first.
