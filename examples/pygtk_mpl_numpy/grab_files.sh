# Download the necessary files
wget -O gtkbundle.zip http://ftp.gnome.org/pub/gnome/binaries/win32/gtk+/2.24/gtk+-bundle_2.24.10-20120208_win32.zip
wget -O pygobject.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pygobject/2.28/pygobject-2.28.3.win32-py2.7.exe
wget -O pycairo.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/1.8/pycairo-1.8.10.win32-py2.7.exe
wget -O pygtk.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-2.24.0.win32-py2.7.exe
#Numpy and Matplotlib are both the bindings for Python 2.7 and 32-bit, but will work on a 64-bit Windows
wget -O numpy.exe http://downloads.sourceforge.net/project/numpy/NumPy/1.9.2/numpy-1.9.2-win32-superpack-python2.7.exe
wget -O matplotlib.exe https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.4.3/windows/matplotlib-1.4.3.win32-py2.7.exe

# GTK runtime
mkdir gtkbundle
unzip -d gtkbundle gtkbundle.zip
cd gtkbundle
rm -r src man include share/doc share/man share/gtk-doc share/gtk-2.0/demo bin/gtk-demo.exe etc/bash_completion.d
cd ..

# Python bindings
mkdir pygobject
unzip -d pygobject pygobject.exe
mkdir pycairo
unzip -d pycairo pycairo.exe
mkdir pygtk
unzip -d pygtk pygtk.exe
mkdir numpy
unzip -d numpy numpy.exe
mkdir matplotlib
unzip -d matplotlib matplotlib.exe

# Reassemble into pynsist_pkgs
echo -n "Assembling GTK files into pynsist_pkgs... "
rm -r pynsist_pkgs
mkdir pynsist_pkgs
mv gtkbundle pynsist_pkgs/gtk

cp -r pygobject/PLATLIB/* pynsist_pkgs
rm -r pygobject

cp -r pycairo/PLATLIB/* pynsist_pkgs
cp -r pycairo/DATA/lib/site-packages/cairo/* pynsist_pkgs/cairo
rm -r pycairo

cp -r pygtk/PLATLIB/* pynsist_pkgs
rm -r pygtk

cp -r matplotlib/PLATLIB/* pynsist_pkgs
rm -r matplotlib

#Unzip numpy into base directory
7z e numpy.exe
#Unzip the NoSSE package into the numpy directory
7z x numpy-1.9.2-nosse.exe -onumpy
cp -r numpy/PLATLIB/* pynsist_pkgs
rm -r numpy

rm -r pynsist_pkgs/gtk-2.0/tests

echo "done"
