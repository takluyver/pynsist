FAQs
====

Building on other platforms
---------------------------

NSIS can run on Linux, so you can build Windows installers without running
Windows. However, if your package relies on compiled extension modules, like
PyQt4, lxml or numpy, you'll need to ensure that the installer is built with
Windows versions of these packages. There are two ways to do this:

- Get the importable packages/modules, either from a Windows installation, or
  by extracting them from an installer. Copy them into a folder called
  ``pynsist_pkgs``, next to your ``installer.cfg`` file. pynsist will
  copy everything in this folder to the build directory.
- Include exe/msi installers for those modules, and modify the ``.nsi`` template
  to extract and run these during installation. This can make your installer
  bigger and slower, and it may create unwanted start menu shortcuts
  (e.g. PyQt4 does), so the first option is usually better. However, if the
  installer sets up other things on the system, you may need to do this.

When running on non-Windows systems, pynsis will bundle a 32-bit version of
Python by default, though you can override this :ref:`in the config file <cfg_python>`.
Whichever method you use, compiled libraries must have the same bit-ness as
the version of Python that's installed.
