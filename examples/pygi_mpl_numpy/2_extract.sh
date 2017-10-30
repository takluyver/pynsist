# Extracts all dependencies and places them in the pynsist_pkgs folder
# You might need to rename the "7z" calls to "7za" depending on your distribution
set -e

mkdir pynsist_pkgs

# Unzip the bindings
7z x pygi.exe -opygi

# Copy the PyGI packages into the pynsist_pkgs folder
# TODO: Update to Python 3.6
7z x pygi/binding/py3.4-64/py3.4-64.7z -obindings
cp -r bindings/* pynsist_pkgs
rm -r bindings

# Copy the noarch and specified architecture dependencies into the gnome folder
array=( ATK Base GDK GDKPixbuf GTK HarfBuzz JPEG Pango WebP TIFF )

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
