Installer details
=================

The installers pynsist builds do a number of things:

1. Unpack and run the Python .msi installer for the version of Python you
   specified.
2. Unpack and run the .msi installer for the `py launcher
   <https://bitbucket.org/vinay.sajip/pylauncher>`_, if you're using Python 2
   (in Python 3, this is installed as part of Python).
3. Install a number of files in the installation directory the user selects:

   - The launcher script(s) that start your application
   - The icon(s) for your application launchers
   - Python packages your application needs
   - Any other files you specified

4. Create a start menu shortcut for each launcher script. If there is only one
   launcher, it will go in the top level of the start menu. If there's more than
   one, the installer will make a folder named after the application.
5. Write an uninstaller, and the registry keys to put it in 'Add/remove programs'.
   The uninstaller only uninstalls your application (undoing steps 3-5); it
   leaves Python alone, because there might be other applications using Python.

The installer (and uninstaller) is produced using `NSIS
<http://nsis.sourceforge.net/Main_Page>`_, with the Modern UI.
