import io
import json
from pathlib import Path
import pytest
import re
import responses
from shutil import copytree
from subprocess import run, PIPE
import sys
from testpath import MockCommand, assert_isfile, assert_isdir
from zipfile import ZipFile

from nsist import main
from nsist.util import CACHE_ENV_VAR
from .utils import test_dir, only_on_windows

example_dir = Path(test_dir, 'console_example')

@pytest.fixture()
def console_eg_copy(tmp_path):
    dst = tmp_path / 'example'
    copytree(str(example_dir), str(dst))
    return dst

def respond_python_zip(req):
    buf = io.BytesIO()
    with ZipFile(buf, 'w') as zf:
        zf.writestr('python.exe', b'')
    return 200, {}, buf.getvalue()

@responses.activate
def test_console_example(tmp_path, console_eg_copy, monkeypatch):
    responses.add_callback('GET', re.compile(r'https://www.python.org/ftp/.*'),
        callback=respond_python_zip, content_type='application/zip',
    )

    monkeypatch.chdir(console_eg_copy)
    monkeypatch.setenv(CACHE_ENV_VAR, str(tmp_path / 'cache'))

    with MockCommand('makensis') as makensis:
        ec = main(['installer.cfg'])

    assert ec == 0
    assert makensis.get_calls()[0]['argv'][1].endswith('installer.nsi')

    build_dir = console_eg_copy / 'build' / 'nsis'
    assert_isdir(build_dir)
    assert_isfile(build_dir / 'Python' / 'python.exe')
    assert_isfile(build_dir / 'pkgs' / 'sample_printer' / '__init__.py')
    assert_isfile(build_dir / 'Sample_printer.launch.py')

# To exclude tests requiring network on an unplugged machine, use: pytest -m "not network"

@only_on_windows
@pytest.mark.network
def test_installer(console_eg_copy, tmp_path):
    # Create installer
    run(
        [sys.executable, '-m', 'nsist', 'installer.cfg'],
        cwd=str(console_eg_copy),
        check=True,
    )

    installer = console_eg_copy / 'build' / 'nsis' / 'Guess_the_Number_1.0.exe'
    inst_dir = tmp_path / 'inst'

    # Run installer
    run([str(installer), '/S', '/D={}'.format(inst_dir)], check=True)
    inst_python = inst_dir / 'Python' / 'python.exe'
    inst_launch_script = inst_dir / 'Sample_printer.launch.py'

    assert_isfile(inst_python)
    assert_isfile(inst_launch_script)
    assert_isfile(inst_dir / 'pkgs' / 'sample_printer' / '__init__.py')


    # Run installed program
    res = run([str(inst_python), str(inst_launch_script)],
              check=True, stdout=PIPE)
    json_res = json.loads(res.stdout)

    assert json_res['py_executable'] == str(inst_python)
    assert json_res['py_version'].startswith('3.6.3')  # Set in installer.cfg
    assert json_res['data_file_path'].endswith('data.txt')
    assert json_res['data_file_content'] == 'newt'
