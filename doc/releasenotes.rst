Release notes
=============

Version 2.5.1
-------------

* Fix locating the ``pkgs`` subdirectory in command-line launchers
  (:ghpull:`200`).

Version 2.5
-----------

* Make more modern installers, with unicode support and DPI awareness
  (less blurry) when using NSIS version 3 (:ghpull:`189`).
* Assemble wrapper executables for commands at build time, rather than on
  installation. This is possible thanks to Vinay Sajip adding support for
  paths from the launcher directory to the launcher bases (:ghpull:`191`).
* An integration test checks creating an installer, installing and running a
  simple program (:ghpull:`190`).

Version 2.4
-----------

* :ref:`command_config` can now include ``console=false`` to make a command on
  :envvar:`PATH` which runs without a console window (:ghpull:`179`).
* Fix for using ``pywin32`` in installed code launched from a command
  (:ghpull:`175`).
* Work around wheels where some package data files are shipped in a way that
  assumes the default pip install layout (:ghpull:`172`).

Version 2.3
-----------

* Command line exes are now based on the launchers made by Vinay Sajip for
  `distlib <https://distlib.readthedocs.io/en/latest/>`_, instead of the
  launchers from setuptools. They should be more robust with spaces in paths
  (:ghpull:`169`).
* Fixed excluding entire folders extracted from wheels (:ghissue:`168`).
* When doing a per-user install of an application with commands, the ``PATH``
  environment variable is modified just for that user (:ghpull:`170`).

Version 2.2
-----------

* New ``local_wheels`` option to include packages from wheel ``.whl`` files
  by path (:ghpull:`164`).
* ``.dist-info`` directories from wheels are now installed alongside the
  importable packages, allowing plugin discovery mechanisms based on *entry
  points* to work (:ghpull:`161`).
* Fixed including multiple files with the same name to be installed to different
  folders (:ghpull:`162`).
* The ``exclude`` option now works to exclude files extracted from wheels
  (:ghpull:`147`).
* ``exclude`` patterns work with either slash ``/`` or backslash ``\`` as
  separators, independent of the platform on which you build the installer
  (:ghpull:`148`).
* Destination paths for the ``files`` include option now work with slashes
  as well as backslashes (:ghpull:`158`).
* ``extra_preamble`` for start menu shortcuts can now use the ``installdir``
  variable to get the installation directory. This was already available for
  commands, so the change makes it easier to use a single preamble for both
  (:ghpull:`149`).
* Test infrastructure switched to pytest and tox (:ghpull:`165`).
* New FAQ entry on :ref:`faq-tkinter` (:ghpull:`146`).

Version 2.1
-----------

* Ensure that if an icon is specified it will be used during install and
  uninstall, and as the icon for the installer itself (:ghpull:`143`).
* Add handling of a license file. If a ``license_file`` is given in the
  ``Application`` section of the configuration file an additional step will take
  place before installation to check the user's agreement to abide by the
  displayed license. If the license is not given, the extra step is omitted
  (the default behaviour) (:ghpull:`143`).
* Fix for launching Python subprocesses with the installed packages available
  for import (:ghpull:`142`).
* Ensure ``.pth`` files in the installed packages directory are read
  (:ghpull:`138`).

Version 2.0
-----------

Pynsist 2 only supports 'bundled' Python, and therefore only Python 3.5 and
above. For 'installer' format Python and older Python versions, use Pynsist 1.x
(``pip install pynsist<2``).

* Pynsist installers can now install into a per-user directory, allowing them
  to be used without admin access.
* Get wheels for the installer from local directories, by listing the
  directories in ``extra_wheel_sources`` in the ``[Include]`` section.
* Better error message when copying fails on a namespace package.

Version 1.12
------------

* Fix a bug with unpacking wheels on Python 2.7, by switching to ``pathlib2``
  for the pathlib backport.

Version 1.11
------------

* Lists in the config file, such as ``packages`` and ``pypi_wheels`` can now
  begin on the line after the key.
* Clearer error if the specified config file is not found.

Version 1.10
------------

* New optional field ``publisher``, to provide a publisher name in the uninstall
  list.
* The uninstall information in the registry now also includes ``DisplayVersion``.
* The directory containing ``python.exe`` is now added to the ``%PATH%``
  environment variable when your application runs. This fixes a DLL loading
  issue for PyQt5 if you use bundled Python.
* When installing a 64-bit application, the uninstall registry keys are now
  added to the 64-bit view of the registry.
* Fixed an error when using wheels which install files into the same package,
  such as ``PyQt5`` and ``PyQtChart``.
* Issue a warning when we can't find the cache directory on Windows.

Version 1.9
-----------

* When building an installer with Python 3.6 or above, bundled Python
  is now the default. For Python up to 3.5, 'installer' remains
  the default format. You can override the default by specifying ``format`` in
  the :ref:`cfg_python` of the config file.
* The C Runtime needed for bundled Python is now installed 'app-local', rather
  than downloading and installing Windows Update packages at install time. This
  is considerably simpler, but the app-local runtime will not be updated by
  Windows Update. A new ``include_msvcrt`` config option allows the developer to
  exclude the app-local runtime - their applications will then depend on the
  runtime being installed systemwide.

Version 1.8
-----------

* New example applications using:
  - PyQt5 with QML
  - OpenCV and PyQt5
  - `Pywebview <https://github.com/r0x0r/pywebview>`__
* The code to pick an appropriate wheel now considers wheels with Python version
  specific ABI tags like ``cp35m``, as well as the stable ABI tags like ``abi3``.
* Fixed a bug with fetching a wheel when another version of the same package
  is already cached.
* Fixed a bug in extracting files from certain wheels.
* Installers using bundled Python may need a Windows
  update package for the Microsoft C runtime. They now download this from the
  `RawGit <https://rawgit.com/>`__ CDN, rather than hitting GitHub directly.
* If the Windows update package fails to install, an error message will be
  displayed.

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

* Experimental support for creating installers that bundle Python with the
  application.
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
