Release notes
=============

Version 1.7
-----------

* Support for downloading packages as wheels from PyPI, and new
  `PyQt5 <https://github.com/takluyver/pynsist/tree/master/examples/pyqt5>`__ and
  `Pyglet <https://github.com/takluyver/pynsist/tree/master/examples/pyglet>`__
  examples which use this feature.
* Applications can include commands to run at the Windows command prompt. See
  :ref:`command_config`.

Version 1.6
-----------

* Experimental support for creating installers that :ref:`bundle Python with the
  application <python_bundled>`.
* Support for Python 3.5 installers.
* The user agent is set when downloading Python builds, so downloads from
  Pynsist can be identified.
* New example applications using PyGI, numpy and matplotlib.
* Fixed a bug with different path separators in ``exclude`` patterns.

Version 1.5
-----------

* New ``exclude`` option to cut unnecessary files out of directories and
  packages that are copied into the installer.
* The ``installer.nsi`` script is now built using `Jinja <http://jinja.pocoo.org/>`_
  templates instead of a custom templating system. If you have specify a custom
  ``nsi_template`` file, you will need to update it to use Jinja syntax.
* GUI applications (running under :program:`pythonw`) have stdout and stderr
  written to a log file in ``%APPDATA%``. This should catch all ``print``,
  warnings, uncaught errors, and avoid the program freezing if it tries to
  print.
* Applications run in a console (under :program:`python`) now show the traceback
  for an uncaught error in the console as well as writing it to the log file.
* Install :program:`pynsist` command on Windows.
* Fixed an error message caused by unnecessarily rerunning the installer for the
  PEP 397 ``py`` launcher, bundled with Python 2 applications.
* :program:`pynsist` now takes a :option:`--no-makensis` option, which stops it
  before running :program:`makensis` for debugging.

Version 1.0
-----------

* New ``extra_preamble`` option to specify a snippet of Python code to run
  before your main application.
* Packages used in the specified entry points no longer need to be listed
  under the Include section; they are automatically included.
* Write the crash log to a file in ``%APPDATA%``, not in the installation
  directory - on modern Windows, the application can't normally write to its
  install directory.
* Added an example application using pygtk.
* :doc:`installers` documentation added.
* Install Python into ``Program Files\Common Files`` or ``Program Files (x86)\Common Files``,
  so that if both 32- and 64-bit Pythons of the same version are installed,
  neither replaces the other.
* When using 64-bit Python, the application files now go in ``Program Files`` by
  default instead of ``Program Files (x86)``.
* Fixed a bug in finding the NSIS install directory on 64-bit Windows.
* Fixed a bug that prevented using multiprocessing in installed applications.
* Fixed a bug where the ``py.exe`` launcher was not included if you built a
  Python 2 installer using Python 3.
* Better error messages for some invalid input.

Version 0.3
-----------

* Extra files can now be installed into locations other than the installation
  directory.
* Shortcuts can have non-Python commands, e.g. to create a start menu shortcut
  to a help file.
* The Python API has been cleaned up, and there is some :doc:`documentation
  <api/index>` for it.
* Better support for modern versions of Windows:

  * Uninstall shortcuts correctly on Windows Vista and above.
  * Byte compile Python modules at installation, because the ``.pyc`` files
    can't be written when the application runs.

* The Python installers are now downloaded over HTTPS instead of using GPG to
  validate them.
* Shortcuts now launch the application with the working directory set to the
  user's home directory, not the application location.

Version 0.2
-----------

* Python 2 support, thanks to `Johannes Baiter <https://github.com/jbaiter>`_.
* Ability to define multiple shortcuts for one application.
* Validate config files to produce more helpful errors, thanks to
  `Tom Wallroth <https://github.com/devsnd>`_.
* Errors starting the application, such as missing libraries, are now written
  to a log file in the application directory, so you can work out what
  happened.
