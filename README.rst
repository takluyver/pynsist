pynsist is a tool to build Windows installers for your Python applications. The
installers bundle Python itself, so you can distribute your application to
people who don't have Python installed.

At present, pynsist requires Python 3.3 or above, or Python 2.7.

For more information, see `the documentation <http://pynsist.readthedocs.org/en/latest/>`_
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
       version=3.4.0

       [Include]
       # Importable packages that your application requires, one per line
       packages = requests
            bs4
            html5lib

       # Other files and folders that should be installed
       files = LICENSE
           data_files/

3. Run ``pynsist installer.cfg`` to generate your installer. If ``pynsist`` isn't
   found, you can use ``python -m nsist installer.cfg`` instead.
