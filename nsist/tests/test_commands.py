import io
from testpath import assert_isfile, assert_not_path_exists
from zipfile import ZipFile

from nsist import commands, _assemble_launchers

def test_prepare_bin_dir(tmpdir):
    cmds = {
        'acommand': {
            'entry_point': 'somemod:somefunc',
            'extra_preamble': io.StringIO(u'import extra')
        }
    }
    commands.prepare_bin_directory(tmpdir, cmds)

    launcher_file = str(tmpdir / 'launcher_exe.dat')
    launcher_noconsole_file = str(tmpdir / 'launcher_noconsole_exe.dat')
    zip_file = str(tmpdir / 'acommand-append.zip')
    zip_file_invalid = str(tmpdir / 'acommand-append-noconsole.zip')
    exe_file = str(tmpdir / 'acommand.exe')

    assert_isfile(launcher_file)
    assert_isfile(launcher_noconsole_file)
    assert_isfile(zip_file)
    assert_not_path_exists(zip_file_invalid)
    assert_not_path_exists(exe_file)

    with open(launcher_file, 'rb') as lf:
        b_launcher = lf.read()
        assert b_launcher[:2] == b'MZ'
    with open(launcher_noconsole_file, 'rb') as lf:
        assert lf.read(2) == b'MZ'

    with ZipFile(zip_file) as zf:
        assert zf.testzip() is None
        script_contents = zf.read('__main__.py').decode('utf-8')
    assert 'import extra' in script_contents
    assert 'somefunc()' in script_contents

    _assemble_launchers.main(['_assemble_launchers.py', 'C:\\path\\to\\python', str(tmpdir)])

    assert_isfile(exe_file)

    with open(exe_file, 'rb') as ef, open(zip_file, 'rb') as zf:
        b_exe = ef.read()
        b_zip = zf.read()
        assert b_exe[:len(b_launcher)] == b_launcher
        assert b_exe[len(b_launcher):-len(b_zip)].decode('utf-8') == '#!"C:\\path\\to\\python.exe"\r\n'
        assert b_exe[-len(b_zip):] == b_zip

    with ZipFile(exe_file) as zf:
        assert zf.testzip() is None
        assert zf.read('__main__.py').decode('utf-8') == script_contents

def test_prepare_bin_dir_noconsole(tmpdir):
    cmds = {
        'acommand': {
            'entry_point': 'somemod:somefunc',
            'console': False
        }
    }
    commands.prepare_bin_directory(tmpdir, cmds)

    launcher_file = str(tmpdir / 'launcher_exe.dat')
    launcher_noconsole_file = str(tmpdir / 'launcher_noconsole_exe.dat')
    zip_file = str(tmpdir / 'acommand-append-noconsole.zip')
    zip_file_invalid = str(tmpdir / 'acommand-append.zip')
    exe_file = str(tmpdir / 'acommand.exe')

    assert_isfile(launcher_file)
    assert_isfile(launcher_noconsole_file)
    assert_isfile(zip_file)
    assert_not_path_exists(zip_file_invalid)
    assert_not_path_exists(exe_file)

    with open(launcher_file, 'rb') as lf:
        assert lf.read(2) == b'MZ'
    with open(launcher_noconsole_file, 'rb') as lf:
        b_launcher = lf.read()
        assert b_launcher[:2] == b'MZ'

    with ZipFile(zip_file) as zf:
        assert zf.testzip() is None
        script_contents = zf.read('__main__.py').decode('utf-8')
    assert 'import extra' not in script_contents
    assert 'somefunc()' in script_contents

    _assemble_launchers.main(['_assemble_launchers.py', 'C:\\custom\\python.exe', str(tmpdir)])

    assert_isfile(exe_file)

    with open(exe_file, 'rb') as ef, open(zip_file, 'rb') as zf:
        b_exe = ef.read()
        b_zip = zf.read()
        assert b_exe[:len(b_launcher)] == b_launcher
        assert b_exe[len(b_launcher):-len(b_zip)].decode('utf-8') == '#!"C:\\custom\\pythonw.exe"\r\n'
        assert b_exe[-len(b_zip):] == b_zip

    with ZipFile(exe_file) as zf:
        assert zf.testzip() is None
        assert zf.read('__main__.py').decode('utf-8') == script_contents
