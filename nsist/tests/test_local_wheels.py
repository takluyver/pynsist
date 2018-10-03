import glob
import os
from pathlib import Path
import platform
import subprocess

import pytest
from testpath import assert_isfile, assert_isdir

from nsist.wheels import WheelGetter

# To exclude tests requiring network on an unplugged machine, use: pytest -m "not network"

@pytest.mark.network
def test_matching_one_pattern(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    subprocess.call(['pip', 'wheel', 'requests==2.19.1', '-w', str(td1)])

    wg = WheelGetter([], [os.path.join(td1, '*.whl')], td2, platform.python_version(), 64)
    wg.get_globs()

    assert_isdir(os.path.join(td2, 'requests'))
    assert_isfile(os.path.join(td2, 'requests-2.19.1.dist-info', 'METADATA'))

    assert_isdir(os.path.join(td2, 'urllib3'))
    assert glob.glob(os.path.join(td2, 'urllib3*.dist-info'))

@pytest.mark.network
def test_duplicate_wheel_files_raise(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    subprocess.call(['pip', 'wheel', 'requests==2.19.1', '-w', str(td1)])

    wg = WheelGetter(['requests==2.19.1'], [os.path.join(td1, '*.whl')], td2,
                     platform.python_version(), 64)

    with pytest.raises(ValueError, match='Multiple wheels specified'):
        wg.get_all()

def test_invalid_wheel_file_raise(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    open(os.path.join(td1, 'notawheel.txt'), 'w+')

    wg = WheelGetter([], [os.path.join(td1, '*')], td2,
                     platform.python_version(), 64)

    with pytest.raises(ValueError, match='notawheel.txt'):
        wg.get_globs()

def test_incompatible_platform_wheel_file_raise(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    Path(td1, 'incompatiblewheel-1.0.0-py2.py3-none-linux_x86_64.whl').touch()

    wg = WheelGetter([], [os.path.join(td1, '*.whl')], td2,
                     platform.python_version(), 64)

    with pytest.raises(ValueError, match='not compatible with .* win_amd64'):
        wg.get_globs()

def test_incompatible_python_wheel_file_raise(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    Path(td1, 'incompatiblewheel-1.0.0-py26-none-any.whl').touch()

    wg = WheelGetter([], [os.path.join(td1, '*.whl')], td2,
                     platform.python_version(), 64)

    with pytest.raises(ValueError, match='not compatible with Python {}'
                       .format(platform.python_version())):
        wg.get_globs()

def test_useless_wheel_glob_path_raise(tmpdir):
    td1 = str(tmpdir.mkdir('wheels'))
    td2 = str(tmpdir.mkdir('pkgs'))

    wg = WheelGetter([], [os.path.join(td1, '*.whl')], td2, '3.6', 64)

    with pytest.raises(ValueError, match='does not match any files'):
        wg.get_globs()
