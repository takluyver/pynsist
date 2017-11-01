pynsist |version|
=================

Pynsist is a tool to build Windows installers for your Python applications. The
installers bundle Python itself, so you can distribute your application to
people who don't have Python installed.

Pynsist 2 requires Python 3.5 or above.
You can use `Pynsist 1.x <http://pynsist.readthedocs.io/en/1.12/>`_ on
Python 2.7 and Python 3.3 or above.

Quickstart
----------

1. Get the tools. Install `NSIS <http://nsis.sourceforge.net/Download>`_, and
   then install pynsist from PyPI by running ``pip install pynsist``.

2. Write a config file ``installer.cfg``, like this:

   .. code-block:: ini
   
       [Application]
       name=My App
       version=1.0
       # How to launch the app - this calls the 'main' function from the 'myapp' package:
       entry_point=myapp:main
       icon=myapp.ico

       [Python]
       version=3.6.3

       [Include]
       # Packages from PyPI that your application requires, one per line
       # These must have wheels on PyPI:
       pypi_wheels = requests==2.18.4
            beautifulsoup4==4.6.0
            html5lib==0.999999999

       # Other files and folders that should be installed
       files = LICENSE
           data_files/

   See :doc:`cfgfile` for more details about this, including how to bundle
   packages which don't publish wheels.

3. Run ``pynsist installer.cfg`` to generate your installer. If ``pynsist`` isn't
   found, you can use ``python -m nsist installer.cfg`` instead.

Contents
--------

.. toctree::
   :maxdepth: 2

   cfgfile
   installers
   faq
   releasenotes
   api/index
   examples
   design

See also the `examples folder <https://github.com/takluyver/pynsist/tree/master/examples>`_
in the repository.

The API is not yet documented here, because I'm still working out how it should
be structured. The functions and classes have docstrings, and you're welcome to
use them directly, though they may change in the future.

.. seealso::

   `pynsist source code on Github <https://github.com/takluyver/pynsist>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

