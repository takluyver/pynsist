Pynsist is a tool to build Windows installers for your Python applications. The
installers bundle Python itself, so you can distribute your application to
people who don't have Python installed.

Pynsist 2 requires Python 3.5 or above.
You can use `Pynsist 1.x <http://pynsist.readthedocs.io/en/1.12/>`_ on
Python 2.7 and Python 3.3 or above.

For more information, see `the documentation <https://pynsist.readthedocs.io/en/latest/>`_
and `the examples <https://github.com/takluyver/pynsist/tree/master/examples>`_.

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

       # To bundle packages which don't publish wheels, or to include directly wheel files
       # from a directory, see the docs on the config file.

       # Other files and folders that should be installed
       files = LICENSE
           data_files/

3. Run ``pynsist installer.cfg`` to generate your installer. If ``pynsist`` isn't
   found, you can use ``python -m nsist installer.cfg`` instead.

This example illustrates how to use Pynsist by itself, for simple projects.
There are other options which can make it easier to integrate as a step in
a more complex build process. See the docs for more information.
