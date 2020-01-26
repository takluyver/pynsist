import io
from testpath import assert_isfile, assert_not_path_exists
from zipfile import ZipFile

from nsist import commands

def test_prepare_bin_dir(tmp_path):
    cmds = {
        'acommand': {
            'entry_point': 'somemod:somefunc',
            'extra_preamble': io.StringIO(u'import extra')
        }
    }
    commands.prepare_bin_directory(tmp_path, cmds)

    exe_file = str(tmp_path / 'acommand.exe')

    assert_isfile(exe_file)

    with open(commands.find_exe(console=True), 'rb') as lf:
        b_launcher = lf.read()
        assert b_launcher[:2] == b'MZ'  # Sanity check

    with open(exe_file, 'rb') as ef:
        b_exe = ef.read()
        assert b_exe[:len(b_launcher)] == b_launcher
        assert b_exe[len(b_launcher):].startswith(b"#!<launcher_dir>\\..\\Python\\python.exe\r\n")

    with ZipFile(exe_file) as zf:
        assert zf.testzip() is None
        script_contents = zf.read('__main__.py').decode('utf-8')
    assert 'import extra' in script_contents
    assert 'somefunc()' in script_contents

def test_prepare_bin_dir_noconsole(tmp_path):
    cmds = {
        'acommand': {
            'entry_point': 'somemod:somefunc',
            'console': False
        }
    }
    commands.prepare_bin_directory(tmp_path, cmds)

    exe_file = str(tmp_path / 'acommand.exe')

    assert_isfile(exe_file)

    with open(commands.find_exe(console=False), 'rb') as lf:
        b_launcher = lf.read()
        assert b_launcher[:2] == b'MZ'  # Sanity check

    with open(exe_file, 'rb') as ef:
        b_exe = ef.read()
        assert b_exe[:len(b_launcher)] == b_launcher
        assert b_exe[len(b_launcher):].startswith(b"#!<launcher_dir>\\..\\Python\\pythonw.exe\r\n")

    with ZipFile(exe_file) as zf:
        assert zf.testzip() is None
        script_contents = zf.read('__main__.py').decode('utf-8')
    assert 'somefunc()' in script_contents
