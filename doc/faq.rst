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

.. _faq-data-files:

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

.. _faq-subprocess:

Running subprocesses
--------------------

There are a few things to be aware of if your code needs to run a subprocess:

* The ``python`` command may not be found, or may be another version of Python.
  Use :data:`sys.executable` to get the path of the Python executable running
  your application.
* Commands which are normally installed by your Python dependencies, such as
  ``sphinx-build`` or ``pygmentize``, won't be available when your app is
  installed. You can often launch the same thing from an importable
  module by running something like ``{sys.executable} -m sphinx``.
* When your application runs as a GUI (without a console), subprocesses launched
  with :data:`sys.executable` don't have anywhere to write output. This makes
  debugging harder, and the subprocess can get stuck trying to write output.
  You can capture output in your code and print it (sending it to the log file
  described under :ref:`log-file`)::

    res = subprocess.run([sys.executable, "-c", "print('hello')"],
                         text=True, capture_output=True)
    print(res.stdout)
    print(res.stderr)

  If you want a console window to appear for your subprocess, check if
  :data:`sys.executable` points to ``pythonw.exe``, and use ``python.exe`` in
  the same folder instead::

    python = sys.executable
    if python.endswith('pythonw.exe'):
        python = python.removesuffix('pythonw.exe') + 'python.exe'
    subprocess.run([python, "-c", "print('hello'); input('Press enter')"])

  The console will close as soon as the subprocess finishes, so the example
  above uses :func:`input` to wait for input and give the user time to see it.

.. _faq-no-wheels:

Bundling packages which don't have wheels on PyPI
-------------------------------------------------

Most modern Python packages release packages in the 'wheel' format, which
Pynsist can download and use automatically (``pypi_wheels`` in the config file).
But some older packages and packages with certain kinds of complexity don't do
this.

If you need to include a package which doesn't release wheels, you can build
your own wheels and :ref:`include them <cfg_include>` with either the
``extra_wheel_sources`` or the ``local_wheels`` config options.

Run :samp:`pip wheel {package-name}` to build a wheel of a package on PyPI.
If the package contains only Python code, this should always work.

If the package contains compiled extensions (typically C code), and does not
publish wheels on PyPI, you will need to build the wheels on Windows, and you
will need a suitable compiler installed. See `Packaging binary extensions
<https://packaging.python.org/guides/packaging-binary-extensions/>`_ in the
Python packaging user guide for more details. If you're not familiar with
building Python extension modules, this can be difficult, so you might want to
think about whether you can solve the problem without that package.

.. note::

   If a package is maintained but doesn't publish wheels, you could ask its
   maintainers to consider doing so. But be considerate! They may have reasons
   not to publish wheels, it may mean a lot of work for them, and they may have
   been asked before. Don't assume that it's their responsibility to build
   wheels, and do look for existing discussions on the topic before starting a
   new one.

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

``DLL load failed`` errors
--------------------------

Importing compiled extension modules in your application may fail with errors
like this::

    ImportError: DLL load failed: The specified module could not be found.

This means that the Python module it's trying to load needs a DLL which isn't
there. Unfortunately, the error message doesn't say which DLL is missing, and
there's no simple way to identify it.

The traceback should show which import failed. The module that was being
imported should be a file with a ``.pyd`` extension. You can use a program
called `Dependency Walker <https://www.dependencywalker.com/>`_ on this file
to work out what DLLs it needs and which are missing, though you may need to
adjust the 'module search order' to avoid some false negatives.

Once you've worked out what is missing, you'll need to make it available.
This may mean bundling extra DLLs as :ref:`data files <faq-data-files>`.
If you do this, it's up to you to ensure you have the right to redistribute them.

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
