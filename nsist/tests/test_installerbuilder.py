import io
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