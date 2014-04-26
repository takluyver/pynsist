Release notes
=============

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
