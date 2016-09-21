#!/bin/bash
# Download pywin32 for Python 3.5, 64 bit
set -e

if [ ! -f pywin32.exe ]; then
  wget -O pywin32.exe https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/pywin32-220.win-amd64-py3.5.exe
fi

# Comtypes (this is actually pure Python, but it's Windows only,
# so it's easiest to get it like this)
if [ ! -f comtypes.zip ]; then
  wget -O comtypes.zip https://github.com/enthought/comtypes/archive/1.1.3.zip
fi

rm -rf pynsist_pkgs
mkdir pynsist_pkgs

# Unpack pywin32
td=$(mktemp -d)
unzip pywin32.exe -d $td || true  # Suppress some warning/error unzipping
echo "Copying pywin32 files into pynsist_pkgs/"
cp --recursive $td/PLATLIB/* pynsist_pkgs/
rm -r $td

# Unpack comtypes
td=$(mktemp -d)
unzip comtypes.zip -d $td
# If comtypes.gen exists, it gets stuck trying to write there; if not, it
# falls back to %APPDATA%.
rm -r $td/comtypes-*/comtypes/gen/
echo "Running 2to3 on comtypes"
2to3 -wn --no-diffs $td/comtypes-*/comtypes/
echo "Copying comtypes files into pynsist_pkgs/"
cp --recursive $td/comtypes-*/comtypes pynsist_pkgs/
rm -r $td
