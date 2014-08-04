import os
import shutil
import sys
import tempfile
import unittest

pjoin = os.path.join

from .utils import assert_is_file, assert_is_dir, test_dir

running_python = '.'.join(str(x) for x in sys.version_info[:3])

sample_path = [pjoin(test_dir, 'sample_pkgs'),
               pjoin(test_dir, 'sample_zip.egg'),
               pjoin(test_dir, 'sample_zip.egg/rootdir'),
              ]

from nsist.copymodules import copy_modules, ExtensionModuleMismatch


class TestCopyModules(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.target)
    
    def test_copy_plain(self):
        copy_modules(['plainmod', 'plainpkg'], self.target, '3.3.5', sample_path)
        assert_is_file(pjoin(self.target, 'plainmod.py'))
        assert_is_dir(pjoin(self.target, 'plainpkg'))
    
    @unittest.skipIf(sys.platform.startswith("win"), "test for non-Windows platforms")
    def test_copy_wrong_platform(self):
        with self.assertRaisesRegexp(ExtensionModuleMismatch, "will not be usable on Windows"):
            copy_modules(['unix_extmod'], self.target, '3.3.5', sample_path)
        
        with self.assertRaisesRegexp(ExtensionModuleMismatch, "will not be usable on Windows"):
            copy_modules(['unix_extpkg'], self.target, '3.3.5', sample_path)
    
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_copy_windows(self):
        copy_modules(['win_extmod', 'win_extpkg'], self.target, running_python, sample_path)
        assert_is_file(pjoin(self.target, 'win_extmod.pyd'))
        assert_is_dir(pjoin(self.target, 'win_extpkg'))
        
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_copy_wrong_pyversion(self):
        with self.assertRaisesRegexp(ExtensionModuleMismatch, "on Python 4"):
            copy_modules(['win_extpkg'], self.target, '4.0.0', sample_path)
        
        with self.assertRaisesRegexp(ExtensionModuleMismatch, "on Python 4"):
            copy_modules(['win_extmod'], self.target, '4.0.0', sample_path)
    
    def test_copy_from_zipfile(self):
        copy_modules(['zippedmod2','zippedpkg2'],
                     self.target, running_python, sample_path)
#        assert_is_file(pjoin(self.target, 'zippedmod.py'))
#        assert_is_dir(pjoin(self.target, 'zippedpkg'))
        assert_is_file(pjoin(self.target, 'zippedmod2.py'))
        assert_is_dir(pjoin(self.target, 'zippedpkg2'))
    
    def test_module_not_found(self):
        with self.assertRaises(ImportError):
            copy_modules(['nonexistant'], self.target, '3.3.5', sample_path)