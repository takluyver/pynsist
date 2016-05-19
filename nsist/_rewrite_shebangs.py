"""This is run during installation to rewrite the shebang (#! headers) of script
files.
"""
import glob
import os.path
import sys

if sys.version_info[0] >= 3:
    # What do we do if the path contains characters outside the system code page?!
    b_python_exe = sys.executable.encode(sys.getfilesystemencoding())
else:
    b_python_exe = sys.executable

def rewrite(path):
    with open(path, 'rb') as f:
        contents = f.readlines()

    if not contents:
        return
    if contents[0].strip() != b'#!python':
        return

    contents[0] = b'#!"' + b_python_exe + b'"\n'

    with open(path, 'wb') as f:
        f.writelines(contents)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    target_dir = argv[1]
    for path in glob.glob(os.path.join(target_dir, '*-script.py')):
        rewrite(path)

if __name__ == '__main__':
    main()
