"""This is run during installation to assemble command-line exe launchers

Each launcher contains: exe base + shebang + zipped Python code
"""
import glob
import os
import sys

b_shebang = '#!"{}"\r\n'.format(sys.executable).encode('utf-8')

def assemble_exe(path, b_launcher):
    exe_path = path[:-len('-append.zip')] + '.exe'

    with open(exe_path, 'wb') as f:
        f.write(b_launcher)
        f.write(b_shebang)

        with open(path, 'rb') as f2:
            f.write(f2.read())

def main(argv=None):
    if argv is None:
        argv = sys.argv
    target_dir = argv[1]

    with open(os.path.join(target_dir, 'launcher_exe.dat'), 'rb') as f:
        b_launcher = f.read()

    for path in glob.glob(os.path.join(target_dir, '*-append.zip')):
        assemble_exe(path, b_launcher)

if __name__ == '__main__':
    main()
