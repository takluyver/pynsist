import io

from os.path import join as pjoin

from nsist import InstallerBuilder, DEFAULT_ICON
from .utils import assert_is_file, test_dir


sample_preamble = pjoin(test_dir, u'sample_preamble.py')

def test_prepare_shortcuts(tmpdir):
    shortcuts = {'sc1': {'entry_point': 'norwegian.blue:parrot',
                         'icon': DEFAULT_ICON,
                         'console': False,
                         'extra_preamble': sample_preamble}}
    ib = InstallerBuilder("Test App", "1.0", shortcuts, build_dir=tmpdir)
    ib.prepare_shortcuts()

    scfile = pjoin(tmpdir, 'sc1.launch.pyw')
    assert_is_file(scfile)

    with io.open(scfile, 'r', encoding='utf-8') as f:
        contents = f.read()

    last2lines = [l.strip() for l in contents.rstrip().splitlines()[-2:]]
    assert last2lines == ['from norwegian.blue import parrot', 'parrot()']

    with io.open(sample_preamble, 'r', encoding='utf-8') as f:
        preamble_contents = f.read().strip()

    assert preamble_contents in contents
