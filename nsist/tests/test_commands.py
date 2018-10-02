import io

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # Backport

from nsist import commands, _rewrite_shebangs
from .utils import assert_is_file

cmds = {'acommand': {'entry_point': 'somemod:somefunc',
                     'extra_preamble': io.StringIO(u'import extra')}}

def test_prepare_bin_dir(tmpdir):
    commands.prepare_bin_directory(tmpdir, cmds)
    assert_is_file(str(tmpdir / 'acommand.exe'))
    script_file = tmpdir / 'acommand-script.py'
    assert_is_file(str(script_file))

    with script_file.open() as f:
        script_contents = f.read()
    assert script_contents.startswith("#!python")
    assert 'import extra' in script_contents
    assert 'somefunc()' in script_contents

    _rewrite_shebangs.main(['_rewrite_shebangs.py', str(tmpdir)])
    with script_file.open() as f:
        assert f.read().startswith('#!"')
