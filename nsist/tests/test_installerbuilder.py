import io
import os
from os.path import join as pjoin
from testpath import assert_isfile

from nsist import InstallerBuilder, DEFAULT_ICON
from .utils import test_dir


sample_preamble = pjoin(test_dir, u'sample_preamble.py')

def test_prepare_shortcuts(tmpdir):
    tmpdir = str(tmpdir)
    shortcuts = {'sc1': {'entry_point': 'norwegian.blue:parrot',
                         'icon': DEFAULT_ICON,
                         'console': False,
                         'extra_preamble': sample_preamble}}
    ib = InstallerBuilder("Test App", "1.0", shortcuts, build_dir=tmpdir)
    ib.prepare_shortcuts()

    scfile = pjoin(tmpdir, 'sc1.launch.pyw')
    assert_isfile(scfile)

    with io.open(scfile, 'r', encoding='utf-8') as f:
        contents = f.read()

    last2lines = [l.strip() for l in contents.rstrip().splitlines()[-2:]]
    assert last2lines == ['from norwegian.blue import parrot', 'parrot()']

    with io.open(sample_preamble, 'r', encoding='utf-8') as f:
        preamble_contents = f.read().strip()

    assert preamble_contents in contents

def test_copy_extra_files(tmpdir):
    tmpdir = str(tmpdir)
    files = [
        (pjoin(test_dir, 'data_files', 'dir1', 'eg-data.txt'), '$INSTDIR'),
        (pjoin(test_dir, 'data_files', 'dir2', 'eg-data.txt'), '$INSTDIR\\foo'),
        (pjoin(test_dir, 'data_files', 'dir1', 'subdir'), '$INSTDIR'),
        (pjoin(test_dir, 'data_files', 'dir2', 'subdir'), '$INSTDIR\\foo'),
    ]
    ib = InstallerBuilder("Test App", "1.0", {}, extra_files=files,
                          build_dir=tmpdir)
    ib.copy_extra_files()

    build_dir_files = set(os.listdir(tmpdir))
    for file in ['eg-data.txt', 'eg-data.1.txt', 'subdir', 'subdir.1']:
        assert file in build_dir_files

    assert ib.install_dirs == [
        ('subdir', '$INSTDIR'),
        ('subdir.1', '$INSTDIR\\foo'),
    ]
    assert ib.install_files == [
        ('eg-data.txt', '$INSTDIR'),
        ('eg-data.1.txt', '$INSTDIR\\foo'),
    ]

def test_copy_installer_nsi(tmpdir):
    tmpdir = str(tmpdir)
    files = [
        (pjoin(test_dir, 'data_files', 'dir1', 'installer.nsi'), None),
    ]
    ib = InstallerBuilder("Test App", "1.0", {}, extra_files=files,
                          build_dir=tmpdir)
    ib.copy_extra_files()

    assert_isfile(pjoin(tmpdir, 'installer.1.nsi'))
    assert ib.install_files == [('installer.1.nsi', '$INSTDIR')]
