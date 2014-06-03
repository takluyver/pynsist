# Download the necessary files
wget -O gtkbundle.zip http://ftp.gnome.org/pub/gnome/binaries/win32/gtk+/2.24/gtk+-bundle_2.24.10-20120208_win32.zip
wget -O pygobject.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pygobject/2.28/pygobject-2.28.3.win32-py2.7.exe
wget -O pycairo.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/1.8/pycairo-1.8.10.win32-py2.7.exe
wget -O pygtk.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-2.24.0.win32-py2.7.exe

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

rm -r pynsist_pkgs/gtk-2.0/tests

echo "done"
