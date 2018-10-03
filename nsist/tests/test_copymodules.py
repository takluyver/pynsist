import os
import sys

import pytest
from testpath import assert_isfile, assert_isdir

from nsist.copymodules import copy_modules, ExtensionModuleMismatch
from .utils import test_dir, skip_on_windows, only_on_windows

pjoin = os.path.join
running_python = '.'.join(str(x) for x in sys.version_info[:3])

sample_path = [pjoin(test_dir, 'sample_pkgs'),
               pjoin(test_dir, 'sample_zip.egg'),
               pjoin(test_dir, 'sample_zip.egg/rootdir'),
              ]


def test_copy_plain(tmpdir):
    tmpdir = str(tmpdir)
    copy_modules(['plainmod', 'plainpkg'], tmpdir, '3.3.5', sample_path)
    assert_isfile(pjoin(tmpdir, 'plainmod.py'))
    assert_isdir(pjoin(tmpdir, 'plainpkg'))

@skip_on_windows
def test_copy_wrong_platform(tmpdir):
    tmpdir = str(tmpdir)
    with pytest.raises(ExtensionModuleMismatch, match="will not be usable on Windows"):
        copy_modules(['unix_extmod'], tmpdir, '3.3.5', sample_path)

    with pytest.raises(ExtensionModuleMismatch, match="will not be usable on Windows"):
        copy_modules(['unix_extpkg'], tmpdir, '3.3.5', sample_path)

@only_on_windows
def test_copy_windows(tmpdir):
    tmpdir = str(tmpdir)
    copy_modules(['win_extmod', 'win_extpkg'], tmpdir, running_python, sample_path)
    assert_isfile(pjoin(tmpdir, 'win_extmod.pyd'))
    assert_isdir(pjoin(tmpdir, 'win_extpkg'))

@only_on_windows
def test_copy_wrong_pyversion(tmpdir):
    tmpdir = str(tmpdir)
    with pytest.raises(ExtensionModuleMismatch, match="on Python 4"):
        copy_modules(['win_extpkg'], tmpdir, '4.0.0', sample_path)

    with pytest.raises(ExtensionModuleMismatch, match="on Python 4"):
        copy_modules(['win_extmod'], tmpdir, '4.0.0', sample_path)

def test_copy_from_zipfile(tmpdir):
    tmpdir = str(tmpdir)
    copy_modules(['zippedmod2', 'zippedpkg2'],
                 tmpdir, running_python, sample_path)
#        assert_isfile(pjoin(tmpdir, 'zippedmod.py'))
#        assert_isdir(pjoin(tmpdir, 'zippedpkg'))
    assert_isfile(pjoin(tmpdir, 'zippedmod2.py'))
    assert_isdir(pjoin(tmpdir, 'zippedpkg2'))

def test_module_not_found(tmpdir):
    tmpdir = str(tmpdir)
    with pytest.raises(ImportError):
        copy_modules(['nonexistant'], tmpdir, '3.3.5', sample_path)
