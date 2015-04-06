# Extracts all dependencies and places them in the pynsist_pkgs folder

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

# Copy the noarch and specified architecture dependencies into the gnome folder
array=( ATK Base GDK GDKPixbuf GTK JPEG Pango WebP TIFF )

for i in "${array[@]}"
do
    echo -e "\nProcessing $i dependency"
    7z x pygi/noarch/$i/$i.data.7z -o$i-noarch
    cp -r $i-noarch/gnome/* pynsist_pkgs/gnome
    rm -r $i-noarch

    7z x pygi/rtvc10-64/$i/$i.bin.7z -o$i-arch
    cp -r $i-arch/gnome/* pynsist_pkgs/gnome
    rm -r $i-arch
done

#Remove pygi Folder
rm -r pygi

#Compile glib schemas
glib-compile-schemas pynsist_pkgs/gnome/share/glib-2.0/schemas/
