import glob
import os
import platform
import subprocess

import pytest

from nsist.pypi import fetch_pypi_wheels
from .utils import assert_is_dir, assert_is_file

# To exclude tests requiring network on an unplugged machine, use: pytest -m "not network"

@pytest.mark.network
def test_matching_one_pattern(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    subprocess.call(['pip', 'wheel', 'requests==2.19.1', '-w', str(td1)])

    fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

    assert_is_dir(os.path.join(td2, 'requests'))
    assert_is_file(os.path.join(td2, 'requests-2.19.1.dist-info', 'METADATA'))

    assert_is_dir(os.path.join(td2, 'urllib3'))
    assert glob.glob(os.path.join(td2, 'urllib3*.dist-info'))

@pytest.mark.network
def test_duplicate_wheel_files_raise(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    subprocess.call(['pip', 'wheel', 'requests==2.19.1', '-w', str(td1)])

    with pytest.raises(ValueError, match='wheel distribution requests already included'):
        fetch_pypi_wheels(['requests==2.19.1'],
                          [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

def test_invalid_wheel_file_raise(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    open(os.path.join(td1, 'notawheel.txt'), 'w+')

    with pytest.raises(ValueError, match='Invalid wheel file name: notawheel.txt'):
        fetch_pypi_wheels([], [os.path.join(td1, '*')], td2, platform.python_version(), 64)

def test_incompatible_plateform_wheel_file_raise(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    open(os.path.join(td1, 'incompatiblewheel-1.0.0-py2.py3-none-linux_x86_64.whl'), 'w+')

    with pytest.raises(ValueError, match='{0} is not compatible with Python {1} for Windows'
                       .format('incompatiblewheel-1.0.0-py2.py3-none-linux_x86_64.whl',
                               platform.python_version())):
        fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

def test_incompatible_python_wheel_file_raise(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    open(os.path.join(td1, 'incompatiblewheel-1.0.0-py26-none-any.whl'), 'w+')

    with pytest.raises(ValueError, match='{0} is not compatible with Python {1} for Windows'
                       .format('incompatiblewheel-1.0.0-py26-none-any.whl',
                               platform.python_version())):
        fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)

def test_useless_wheel_glob_path_raise(tmpdir):
    td1 = tmpdir.mkdir('wheels')
    td2 = tmpdir.mkdir('pkgs')

    with pytest.raises(ValueError, match='does not match any wheel file'):
        fetch_pypi_wheels([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)
