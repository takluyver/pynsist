import io
import unittest

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # Backport

from testpath.tempdir import TemporaryDirectory
from testpath import assert_isfile

from nsist import commands, _rewrite_shebangs

cmds = {'acommand': {
                'entry_point': 'somemod:somefunc',
                'extra_preamble': io.StringIO(u'import extra')
           }}

class TestCommands(unittest.TestCase):
    def test_prepare_bin_dir(self):
        with TemporaryDirectory() as td:
            td = Path(td)
            commands.prepare_bin_directory(td, cmds)
            assert_isfile(str(td / 'acommand.exe'))
            script_file = td / 'acommand-script.py'
            assert_isfile(str(script_file))

            with script_file.open() as f:
                script_contents = f.read()
            assert script_contents.startswith("#!python")
            self.assertIn('import extra', script_contents)
            self.assertIn('somefunc()', script_contents)

            _rewrite_shebangs.main(['_rewrite_shebangs.py', str(td)])
            with script_file.open() as f:
                assert f.read().startswith('#!"')
