This is an example that uses PyQt4 binary packages.

To make the installer on a non-Windows system, first run fetch_pyqt_windows.sh.
This will download a PyQt Windows installer from Sourceforge, unpack the files
from it, and copy the necessary ones into pynsist_pkgs where pynsist will
pick them up.

If you want to use PyQt in a '[bundled format](https://pynsist.readthedocs.io/en/latest/cfgfile.html#bundled-python)'
installer with Python 3.5 or later, you'll need to ensure the file `msvcp140.dll`
is included. If you have a Visual Studio installation, you can find it in there;
otherwise download the [Visual C++ Redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=48145).
On Linux, you can extract the DLL from the exe using `cabextract` (after extracting
files from the exe, run it again on a file called `a10`). Place `msvcp140.dll`
inside the `PyQt4` folder, next to files like `QtCore4.dll`.
