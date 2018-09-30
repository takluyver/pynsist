import io
import os
from os.path import join as pjoin
import shutil
import tempfile
import unittest

from .utils import assert_is_file, test_dir
from nsist import InstallerBuilder, DEFAULT_ICON

sample_preamble = pjoin(test_dir, u'sample_preamble.py')

class TestInstallerBuilder(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.target)
    
    def test_prepare_shortcuts(self):
        shortcuts = {'sc1': {'entry_point': 'norwegian.blue:parrot',
                             'icon': DEFAULT_ICON,
                             'console': False,
                             'extra_preamble': sample_preamble,
                             }
                    }
        ib = InstallerBuilder("Test App", "1.0", shortcuts, build_dir=self.target)
        ib.prepare_shortcuts()
        
        scfile = pjoin(self.target, 'sc1.launch.pyw')
        assert_is_file(scfile)
        
        with io.open(scfile, 'r', encoding='utf-8') as f:
            contents = f.read()
        
        last2lines = [l.strip() for l in contents.rstrip().splitlines()[-2:]]
        assert last2lines == ['from norwegian.blue import parrot', 'parrot()']
        
        with io.open(sample_preamble, 'r', encoding='utf-8') as f:
            preamble_contents = f.read().strip()
        
        assert preamble_contents in contents

    def test_copy_files(self):
        files = [
            (pjoin(test_dir, 'data_files', 'dir1', 'eg-data.txt'), '$INSTDIR'),
            (pjoin(test_dir, 'data_files', 'dir2', 'eg-data.txt'), '$INSTDIR\\foo'),
            (pjoin(test_dir, 'data_files', 'dir1', 'subdir'), '$INSTDIR'),
            (pjoin(test_dir, 'data_files', 'dir2', 'subdir'), '$INSTDIR\\foo'),
        ]
        ib = InstallerBuilder("Test App", "1.0", {}, extra_files=files,
                              build_dir=self.target)
        ib.copy_extra_files()

        build_dir_files = set(os.listdir(self.target))
        self.assertEqual(build_dir_files,
                         {'eg-data.txt', 'eg-data.1.txt', 'subdir', 'subdir.1'})

        self.assertEqual(ib.install_dirs, [
            ('subdir', '$INSTDIR'),
            ('subdir.1', '$INSTDIR\\foo'),
        ])
        self.assertEqual(ib.install_files, [
            ('eg-data.txt', '$INSTDIR'),
            ('eg-data.1.txt', '$INSTDIR\\foo'),
        ])
