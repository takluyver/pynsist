Example applications
====================

Simplified examples
-------------------

The repository contains a number of simple examples for building applications
with different frameworks:

- `A console application <https://github.com/takluyver/pynsist/tree/master/examples/console>`_
- `A tkinter application <https://github.com/takluyver/pynsist/tree/master/examples/tkinter>`_
- `A PyQt4 application <https://github.com/takluyver/pynsist/tree/master/examples/pyqt>`_
- `A PyGTK application <https://github.com/takluyver/pynsist/tree/master/examples/pygtk>`_
- `A PyGTK application including Numpy and Matplotlib (32 bit, Python 2.7) <https://github.com/takluyver/pynsist/tree/master/examples/pygtk_mpl_numpy>`_
- `A pygame application <https://github.com/takluyver/pynsist/tree/master/examples/pygame>`_

Real-world examples
-------------------

These may illustrate more complex uses of pynsist.

- The author's own application, `Taxonome <https://bitbucket.org/taxonome/taxonome/src>`_,
  is a Python 3, PyQt4 application for working with scientific names for species.
- `Spreads <https://github.com/jbaiter/spreads/tree/windows>`_ is a book scanning tool,
  including a tkinter configuration system and a local webserver. Its use of
  pynsist (see ``buildmsi.py``) includes working with setuptools info files.
- `InnStereo <https://github.com/tobias47n9e/innsbruck-stereographic>`_ is a GTK 3
  application for geologists. Besides pygi, it uses numpy and matplotlib.
