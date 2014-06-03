This is an example of building a Windows installer for a pygtk application. This
is a bit more complex than the other examples, because the GTK runtime needs to
be set up. This needs two things:

1. The pieces of the GTK runtime and its Python bindings. The script ``grab_files.sh``
   downloads these, unpacks them, trims out unnecessary pieces, and places them
   where pynsist will find them.
2. The ``PATH`` environment variable must be modified before we try to import
   the Python GTK bindings. This is done by the ``extra_preamble`` field in
   ``installer.cfg``.

I referred to the following sources of information to work this out:

Bundling pygtk using py2exe:
http://faq.pygtk.org/index.py?file=faq21.005.htp&req=show
https://web.archive.org/web/20060208162511/http://www.anti-particle.com/py2exe-0.5.shtml

Installing pygtk & deps: http://www.pygtk.org/downloads.html
(inc links for pygtk, pycairo and pygobject installers)

GTK bundles for Windows: http://www.gtk.org/download/win32.php
