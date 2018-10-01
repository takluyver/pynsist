FAQs
====

Building on other platforms
---------------------------

You can use Pynsist to build Windows installers from a Linux or Mac system.
You'll need to install NSIS so that the ``makensis`` command is available.
Here's how to do that on some common platforms:

* Debian/Ubuntu: ``sudo apt-get install nsis``
* Fedora: ``sudo dnf install mingw32-nsis``
* Mac with `Homebrew <https://brew.sh/>`__: ``brew install makensis``

Installing Pynsist itself is the same on all platforms::

    pip install pynsist

If your package relies on compiled extension modules, like
PyQt4, lxml or numpy, you'll need to ensure that the installer is built with
Windows versions of these packages. There are a few options for this:

- List them under ``pypi_wheels`` in the :ref:`Include section <cfg_include>`
  of your config file. Pynsist will download Windows-compatible wheels from
  PyPI. This is the easiest option if the dependency publishes wheels.
- Get the importable packages/modules, either from a Windows installation, or
  by extracting them from an installer. Copy them into a folder called
  ``pynsist_pkgs``, next to your ``installer.cfg`` file. Pynsist will
  copy everything in this folder to the build directory.
- Include exe/msi installers for those modules, and modify the ``.nsi`` template
  to extract and run these during installation. This can make your installer
  bigger and slower, and it may create unwanted start menu shortcuts
  (e.g. PyQt4 does), so it's a last resort. However, if the
  installer sets up other things on the system, you may need to do this.

When running on non-Windows systems, Pynsist will bundle a 32-bit version of
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
application (``sys.modules['__main__'].__file__``).

.. note::

   The techniques above work for fixed data files which you ship with your
   application. For files which your app will *write*, you should use another
   location, because an app installed systemwide cannot write files in its
   install directory. Use the ``APPDATA`` or ``LOCALAPPDATA`` environment
   variables as locations to write hidden data files (`what's the difference?
   <https://superuser.com/a/21462/209976>`__)::

       writable_file = os.path.join(os.environ['LOCALAPPDATA'], 'MyApp', 'file.dat')

.. _faq-tkinter:

Packaging with tkinter
----------------------

Because Pynsist makes use of the "bundled" versions of Python the ``tkinter``
module isn't included by default. If your application relies on ``tkinter`` for
a GUI then you need to find the following assets:

* The ``tcl`` directory in the root directory of a Windows installation of
  Python. This needs to come from the same Python version and bitness (i.e.
  32-bit or 64-bit) as the Python you are bundling into the installer.
* The ``_tkinter.pyd``, ``tcl86t.dll`` and ``tk86t.dll`` libraries in the
  ``DLLs`` directory of the version of Python your are using in your app. As
  above, these must be the same bitness and version as your target version of
  Python.
* The ``_tkinter.lib`` file in the ``libs`` directory of the version of Python
  you are using in your app. Same caveats as above.

The ``tcl`` directory should be copied into the root of your project (i.e. in
the directory that contains ``installer.cfg``) and renamed to ``lib``
(this is important!).

Create a new directory in the root of your project called ``pynsist_pkgs`` and
copy over the other four files mentioned above into it (so it contains
``_tkinter.lib``, ``_tkinter.pyd``, ``tcl86t.dll`` and ``tk86t.dll``).

Finally, in your ``.cfg`` file ensure the ``packages`` section contains
``tkinter`` and ``_tkinter``, and the ``files`` section contains ``lib``, like
this::

    packages=
        tkinter
        _tkinter

    files=lib

Build your installer and test it. You'll know everything is in the right place
if the directory into which your application is installed contains a ``lib``
directory containing the contents of the original ``tcl`` directory and the
``pkgs`` directory contains the remaining four files. If things still don't
work check the bitness and Python version associated with these assets and
make sure they're the same as the version of Python installed with your
application.

.. note::

   A future version of Pynsist might automate some of this procedure to make
   distributing tkinter applications easier.

Code signing
------------

People trying to use your installer will see an 'Unknown publisher' warning.
To avoid this, you can sign it with a digital certificate. See
`Mozilla's instructions on signing executables using Mono
<https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Build_Instructions/Signing_an_executable_with_Authenticode>`__,
or `this guide from Adafruit on signing an installer
<https://learn.adafruit.com/how-to-sign-windows-drivers-installer/making-an-installer#sign-the-installer>`__.

Signing requires a certificate from a provider trusted by Microsoft.
As of summer 2017, these are the cheapest options I can find:

* Certum's `open source code signing certificate <https://www.certum.eu/certum/cert,offer_en_open_source_cs.xml>`__:
  €86 for a certificate with a smart card and reader, €28 for a new certificate
  if you have the hardware. Each certificate is valid for one year.
  This is only for open source software.
* Many companies resell Comodo code signing certificates at prices lower than
  Comodo themselves, especially if you pay for 3–4 years up front.
  `CodeSignCert <https://codesigncert.com/comodocodesigning>`__ ($59–75 per year),
  `K Software <http://codesigning.ksoftware.net/>`__ ($67–$84 per year) and
  `Cheap SSL Security <https://cheapsslsecurity.co.uk/comodo/codesigningcertificate.html>`__ (UK, £54–£64 per year)
  are a few examples; a search will turn up many more like them.

I haven't used any of these companies, so I'm not making a recommendation.
Please do your own research before buying from them.

If you find another good way to get a code signing certificate, please make a
pull request to add it!


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
Pynsist could do the same thing, but in my experience, this detection is complex and often
misses things, so for now it expects an explicit list of the packages
your application needs.

Another alternative is `conda constructor <https://github.com/conda/constructor>`__,
which builds an installer out of conda packages. Conda packages are more
flexible than PyPI packages, and many libraries are already packaged, but you
have to make a conda package of your own code as well before using conda
constructor to make an installer.
Conda constructor can also make Linux and Mac installers, but unlike Pynsist, it
can't make a Windows installer from Linux or Mac.
