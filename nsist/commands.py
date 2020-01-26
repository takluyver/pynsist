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
    for name, command in commands.items():
        exe_path = target / (name + '.exe')
        console = command.get('console', True)

        # 1. Get the base launcher exe from distlib
        with open(find_exe(bitness, console=console), 'rb') as f:
            launcher_b = f.read()

        # 2. Shebang: Python executable to run with
        # shebangs relative to launcher location, according to
        # https://bitbucket.org/vinay.sajip/simple_launcher/wiki/Launching%20an%20interpreter%20in%20a%20location%20relative%20to%20the%20launcher%20executable
        if console:
            shebang = b"#!<launcher_dir>\\..\\Python\\python.exe\r\n"
        else:
            shebang = b"#!<launcher_dir>\\..\\Python\\pythonw.exe\r\n"

        # 3. The script to run, inside a zip file
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

        zip_bio = io.BytesIO()
        with ZipFile(zip_bio, 'w') as zf:
            zf.writestr('__main__.py', script.encode('utf-8'))

        # Put the pieces together
        with exe_path.open('wb') as f:
            f.write(launcher_b)
            f.write(shebang)
            f.write(zip_bio.getvalue())

