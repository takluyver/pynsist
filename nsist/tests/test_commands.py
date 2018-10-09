import io
from testpath import assert_isfile, assert_not_path_exists
from zipfile import ZipFile

from nsist import commands, _assemble_launchers

cmds = {'acommand': {'entry_point': 'somemod:somefunc',
                     'extra_preamble': io.StringIO(u'import extra')}}

def test_prepare_bin_dir(tmpdir):
    commands.prepare_bin_directory(tmpdir, cmds)

    zip_file = tmpdir / 'acommand-append.zip'
    exe_file = tmpdir / 'acommand.exe'
    assert_isfile(zip_file)
    assert_not_path_exists(exe_file)  # Created by _assemble_launchers

    with ZipFile(str(zip_file)) as zf:
        assert zf.testzip() is None
        script_contents = zf.read('__main__.py').decode('utf-8')
    assert 'import extra' in script_contents
    assert 'somefunc()' in script_contents

    _assemble_launchers.main(['_assemble_launchers.py', str(tmpdir)])

    assert_isfile(exe_file)
    with ZipFile(str(exe_file)) as zf:
        assert zf.testzip() is None
        assert zf.read('__main__.py').decode('utf-8') == script_contents
