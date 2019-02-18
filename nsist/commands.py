import distlib.scripts
import io
import os.path as osp
import shutil
from zipfile import ZipFile


SCRIPT_TEMPLATE = u"""# -*- coding: utf-8 -*-
import sys, os
import site
installdir = os.path.dirname(os.path.dirname(__file__))
pkgdir = os.path.join(installdir, 'pkgs')
sys.path.insert(0, pkgdir)
# Ensure .pth files in pkgdir are handled properly
site.addsitedir(pkgdir)
os.environ['PYTHONPATH'] = pkgdir + os.pathsep + os.environ.get('PYTHONPATH', '')

# Allowing .dll files in Python directory to be found
os.environ['PATH'] += ';' + os.path.dirname(sys.executable)

{extra_preamble}

if __name__ == '__main__':
    from {module} import {func}
    sys.exit({func}())
"""

def find_exe(bitness=32, console=True):
    distlib_dir = osp.dirname(distlib.scripts.__file__)
    name = 't' if console else 'w'
    return osp.join(distlib_dir, '{name}{bitness}.exe'.format(name=name, bitness=bitness))

def prepare_bin_directory(target, commands, bitness=32):
    # Give the base launcher a .dat extension so it doesn't show up as an
    # executable command itself. During the installation it will be copied to
    # each launcher name, and the necessary data appended to it.
    shutil.copy(find_exe(bitness, True), str(target / 'launcher_exe.dat'))
    shutil.copy(find_exe(bitness, False), str(target / 'launcher_noconsole_exe.dat'))

    for name, command in commands.items():
        specified_preamble = command.get('extra_preamble', None)
        if isinstance(specified_preamble, str):
            # Filename
            extra_preamble = io.open(specified_preamble, encoding='utf-8')
        elif specified_preamble is None:
            extra_preamble = io.StringIO()  # Empty
        else:
            # Passed a StringIO or similar object
            extra_preamble = specified_preamble
        module, func = command['entry_point'].split(':')
        script = SCRIPT_TEMPLATE.format(
            module=module, func=func,
            extra_preamble=extra_preamble.read().rstrip(),
        )

        if command.get('console', True):
            append = '-append.zip'
        else:
            append = '-append-noconsole.zip'

        with ZipFile(str(target / (name + append)), 'w') as zf:
            zf.writestr('__main__.py', script.encode('utf-8'))
