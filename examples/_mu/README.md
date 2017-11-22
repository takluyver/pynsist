# Packaging Mu using WiX

This is an experiment. So far, it's nearly but not quite working.

To build the MSI package:

1. Run `pynsist installer.cfg --no-makensis` to assemble the necessary files.
2. Run `prep_files.py` in this folder to move some files and call 'heat' to
   make a list of the files.
3. Run `wixit.py` in this folder to build the msi package.