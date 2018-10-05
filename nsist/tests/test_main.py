import io
from pathlib import Path
import re
import responses
from shutil import copy
from testpath import MockCommand, modified_env, assert_isfile, assert_isdir
from testpath.tempdir import TemporaryWorkingDirectory
from zipfile import ZipFile

from nsist import main
from nsist.util import CACHE_ENV_VAR
from .utils import test_dir

example_dir = Path(test_dir, 'console_example')

def respond_python_zip(req):
    buf = io.BytesIO()
    with ZipFile(buf, 'w') as zf:
        zf.writestr('python.exe', b'')
    return 200, {}, buf.getvalue()

@responses.activate
def test_console_example():
    responses.add_callback('GET', re.compile(r'https://www.python.org/ftp/.*'),
        callback=respond_python_zip, content_type='application/zip',
    )

    with TemporaryWorkingDirectory() as td:
        for src in example_dir.iterdir():
            copy(str(src), td)


        with modified_env({CACHE_ENV_VAR: td}), \
             MockCommand('makensis') as makensis:
            ec = main(['installer.cfg'])

        assert ec == 0
        assert makensis.get_calls()[0]['argv'][1].endswith('installer.nsi')

        build_dir = Path(td, 'build', 'nsis')
        assert_isdir(build_dir)
        assert_isfile(build_dir / 'Python' / 'python.exe')
        assert_isfile(build_dir / 'pkgs' / 'guessnumber.py')
        assert_isfile(build_dir / 'Guess_the_Number.launch.py')
