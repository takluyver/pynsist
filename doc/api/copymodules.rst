Copying Modules and Packages
============================

.. module:: nsist.copymodules

.. class:: ModuleCopier(py_version, path=None)

   Finds and copies importable Python modules and packages.
   
   There is a Python 3 implementation using :mod:`importlib`, and a Python 2
   implementation using :mod:`imp`.
   
   .. method:: copy(modname, target)

      Copy the importable module 'modname' to the directory 'target'.

      modname should be a top-level import, i.e. without any dots.
      Packages are always copied whole.

      This can currently copy regular filesystem files and directories,
      and extract modules and packages from appropriately structured zip
      files.

.. autofunction:: copy_modules
