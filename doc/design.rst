Design principles
=================

or *Why I'm Refusing to Add a Feature*

There are some principles in the design of Pynsist which have led me to turn
down potentially useful options. I've tried to explain them here so that I can
link to this rather than summarising them each time.

1. Pynsist is largely a **simplifying wrapper** around `NSIS
   <http://nsis.sourceforge.net/>`__: it provides an easy way to do a subset of
   the things NSIS can do. All simplifying wrappers come under pressure from
   people who want to do something just outside what the wrapper currently
   covers: they'd love to use the wrapper, if it just had one more option. But
   if we keep adding options, eventually the simplifying wrapper becomes a
   convoluted layer of extra complexity over the original system.

2. I'm very keen to **keep installers as simple as possible**. There are all
   sorts of clever things we could do at install time. But it's much harder to
   write and test the NSIS install code than the Python build code, and errors
   when the end user installs your software are a bigger problem than errors
   when you build it, because you're better able to understand and fix them.
   So Pynsist does as much as possible at build time so that the installer can
   be simple.

3. Pynsist has a **limited scope**: it builds Windows installers for Python
   applications. Mostly GUI applications, but it does also have support for
   adding command-line tools. I don't plan to add support for other target
   platforms or languages.

If you need more flexibility
----------------------------

If you want to do something which Pynsist doesn't support, there are several
ways it can still help you:

- **Generate an nsi script**: You can run Pynsist once with the
  ``--no-makensis`` option. In the build directory, you'll find a file
  ``installer.nsi``, which is the script for your installer. You can modify
  this and run ``makensis installer.nsi`` yourself to build the installer.
- **Write a custom template**: Pynsist uses *Jinja* templates to create the
  nsi script. You can write a custom template and specify it in the
  :ref:`build_config` in your config file. Custom templates can inherit from
  the templates in Pynsist and override blocks, so you have a lot of control
  over the installer this way.
- **Cannibalise the code**: Pull out whatever pieces are useful to you from
  Pynsist and use them in your build scripts. There are the installer templates,
  code to find and download wheels from PyPI, to download Python itself, to
  create command-line entry points, to find ``makensis.exe`` on Windows, and so
  on. You can take specific bits to reuse, or copy the whole thing and apply
  some changes.
