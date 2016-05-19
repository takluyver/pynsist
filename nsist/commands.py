import io
import shutil
import win_cli_launchers

from .util import text_types

SCRIPT_TEMPLATE = u"""#!python
import sys, os
installdir = os.path.dirname(os.path.dirname(__file__))
pkgdir = os.path.join(installdir, 'pkgs')
sys.path.insert(0, pkgdir)
os.environ['PYTHONPATH'] = pkgdir + os.pathsep + os.environ.get('PYTHONPATH', '')

{extra_preamble}

if __name__ == '__main__':
    from {module} import {func}
    {func}()
"""

def prepare_bin_directory(target, commands, bitness=32):
    exe_src = win_cli_launchers.find_exe('x64' if bitness == 64 else 'x86')
    for name, command in commands.items():
        shutil.copy(exe_src, str(target / (name+'.exe')))

        specified_preamble = command.get('extra_preamble', None)
        if isinstance(specified_preamble, text_types):
            # Filename
            extra_preamble = io.open(specified_preamble, encoding='utf-8')
        elif specified_preamble is None:
            extra_preamble = io.StringIO()  # Empty
        else:
            # Passed a StringIO or similar object
            extra_preamble = specified_preamble
        module, func = command['entry_point'].split(':')
        with (target / (name+'-script.py')).open('w') as f:
            f.write(SCRIPT_TEMPLATE.format(
                module=module, func=func,
                extra_preamble=extra_preamble.read().rstrip(),
            ))
