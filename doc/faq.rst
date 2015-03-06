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

Using data files
----------------

Applications often need data files along with their code. The easiest way to use
data files with Pynsist is to store them in a Python package (a directory with
a ``__init__.py`` file) you're creating for your application. They will be
copied automatically, and modules in that package can locate them using
``__file__`` like this::

    data_file_path = os.path.join(os.path.dirname(__file__), 'file.dat')

If you don't want to put data files inside a Python package, you will need to
list them in the ``files`` key of the ``[Include]`` section of the config file.
Your code can find them relative to the location of the launch script running your
application (``sys.module['__main__'].__file__``).

Alternatives
------------

Other ways to distribute applications to users without Python installed include
freeze tools, like `cx_Freeze <http://cx-freeze.sourceforge.net/>`_ and
`PyInstaller <http://www.pyinstaller.org/>`_, and Python compilers like
`Nuitka <http://nuitka.net/>`_.

pynsist has some advantages:

* Python code often does things—like using ``__file__`` to find its
  location on disk, or :data:`sys.executable` to launch Python processes—which
  don't work when it's run from a frozen exe. pynsist just installs Python files,
  so it avoids all these problems.
* It's quite easy to make Windows installers on other platforms, which is
  difficult with other tools.
* The tool itself is simpler to understand, and less likely to need updating for
  new Python versions.

And some disadvantages:

* Installers tend to be bigger because you're bundling the whole Python standard
  library.
* You don't get an exe for your application, just a start menu shortcut to launch
  it.
* pynsist only makes Windows installers.

Popular freeze tools also try to automatically detect what packages you're using.
pynsist could do the same thing, but in my experience, it's complex and often
misses things, so for now it expects an explicit list of the packages
your application needs.
