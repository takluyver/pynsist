import io
from nose.tools import *
from pathlib import Path
from testpath.tempdir import TemporaryDirectory
from testpath import assert_isfile

from nsist import commands, _rewrite_shebangs

cmds = {'acommand': {
                'entry_point': 'somemod:somefunc',
                'extra_preamble': io.StringIO(u'import extra')
           }}

def test_prepare_bin_dir():
    with TemporaryDirectory() as td:
        td = Path(td)
        commands.prepare_bin_directory(td, cmds)
        assert_isfile(td / 'acommand.exe')
        script_file = td / 'acommand-script.py'
        assert_isfile(script_file)

        with script_file.open() as f:
            script_contents = f.read()
        assert script_contents.startswith("#!python")
        assert_in('import extra', script_contents)
        assert_in('somefunc()', script_contents)

        _rewrite_shebangs.main(['_rewrite_shebangs.py', str(td)])
        with script_file.open() as f:
            assert f.read().startswith('#!"')
