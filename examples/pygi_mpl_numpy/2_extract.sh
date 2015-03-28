# Extract files and place them in the pynsist_pkgs folder

mkdir pynsist_pkgs

# Unzip the bindings
7z x numpy.whl -onumpy
7z x matplotlib.exe -omatplotlib
7z x pygi.exe -opygi

# Copy matplotlib and numpy into the pynsist_pkgs folder and delete the folders
cp -r matplotlib/PLATLIB/matplotlib pynsist_pkgs
rm -r matplotlib
cp -r numpy/numpy pynsist_pkgs
rm -r numpy

# Copy the PyGI packages into the pynsist_pkgs folder
7z x pygi/binding/py3.4-64/py3.4-64.7z -obindings
cp -r bindings/* pynsist_pkgs
rm -r bindings

# ATK
7z x pygi/noarch/ATK/ATK.data.7z -oATKnoarch
cp -r ATKnoarch/gnome/* pynsist_pkgs/gnome
rm -r ATKnoarch

7z x pygi/rtvc10-64/ATK/ATK.bin.7z -oATK
cp -r ATK/gnome/* pynsist_pkgs/gnome
rm -r ATK

# Base
7z x pygi/noarch/Base/Base.data.7z -oBasenoarch
cp -r Basenoarch/gnome/* pynsist_pkgs/gnome
rm -r Basenoarch

7z x pygi/rtvc10-64/Base/Base.bin.7z -oBase
cp -r Base/gnome/* pynsist_pkgs/gnome
rm -r Base

# GDK
7z x pygi/noarch/GDK/GDK.data.7z -oGDKnoarch
cp -r GDKnoarch/gnome/* pynsist_pkgs/gnome
rm -r GDKnoarch

7z x pygi/rtvc10-64/GDK/GDK.bin.7z -oGDK
cp -r GDK/gnome/* pynsist_pkgs/gnome
rm -r GDK

# GDKPixbuf
7z x pygi/noarch/GDKPixbuf/GDKPixbuf.data.7z -oGDKPixbufnoarch
cp -r GDKPixbufnoarch/gnome/* pynsist_pkgs/gnome
rm -r GDKPixbufnoarch

7z x pygi/rtvc10-64/GDKPixbuf/GDKPixbuf.bin.7z -oGDKPixbuf
cp -r GDKPixbuf/gnome/* pynsist_pkgs/gnome
rm -r GDKPixbuf

# GTK
7z x pygi/noarch/GTK/GTK.data.7z -oGTKnoarch
cp -r GTKnoarch/gnome/* pynsist_pkgs/gnome
rm -r GTKnoarch

7z x pygi/rtvc10-64/GTK/GTK.bin.7z -oGTK
cp -r GTK/gnome/* pynsist_pkgs/gnome
rm -r GTK

# JPEG
7z x pygi/noarch/JPEG/JPEG.data.7z -oJPEGnoarch
cp -r JPEGnoarch/gnome/* pynsist_pkgs/gnome
rm -r JPEGnoarch

7z x pygi/rtvc10-64/JPEG/JPEG.bin.7z -oJPEG
cp -r JPEG/gnome/* pynsist_pkgs/gnome
rm -r JPEG

# Pango
7z x pygi/noarch/Pango/Pango.data.7z -oPangonoarch
cp -r Pangonoarch/gnome/* pynsist_pkgs/gnome
rm -r Pangonoarch

7z x pygi/rtvc10-64/Pango/Pango.bin.7z -oPango
cp -r Pango/gnome/* pynsist_pkgs/gnome
rm -r Pango

# WebP
7z x pygi/noarch/WebP/WebP.data.7z -oWebPnoarch
cp -r WebPnoarch/gnome/* pynsist_pkgs/gnome
rm -r WebPnoarch

7z x pygi/rtvc10-64/WebP/WebP.bin.7z -oWebP
cp -r WebP/gnome/* pynsist_pkgs/gnome
rm -r WebP

# TIFF
7z x pygi/noarch/TIFF/TIFF.data.7z -oTIFFnoarch
cp -r TIFFnoarch/gnome/* pynsist_pkgs/gnome
rm -r TIFFnoarch

7z x pygi/rtvc10-64/TIFF/TIFF.bin.7z -oTIFF
cp -r TIFF/gnome/* pynsist_pkgs/gnome
rm -r TIFF

#Remove pygi Folder
rm -r pygi
