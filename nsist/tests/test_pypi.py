from os.path import join as pjoin
from pathlib import Path
import pytest

from nsist.pypi import (
    WheelLocator, extract_wheel, CachedRelease, merge_dir_to, NoWheelError,
)
from .utils import assert_is_file

# To exclude tests requiring network on an unplugged machine, use: pytest -m "not network"

@pytest.mark.network
def test_download(tmpdir):
    wd = WheelLocator("astsearch==0.1.2", "3.5.1", 64)
    wheel = wd.fetch()
    assert_is_file(str(wheel))

    extract_wheel(wheel, target_dir=tmpdir)
    assert_is_file(pjoin(tmpdir, 'astsearch.py'))
    assert_is_file(pjoin(tmpdir, 'astsearch-0.1.2.dist-info', 'METADATA'))

@pytest.mark.network
def test_bad_name():
    # Packages can't be named after stdlib modules like os
    wl = WheelLocator("os==1.0", "3.5.1", 64)
    with pytest.raises(NoWheelError):
        wl.get_from_pypi()

@pytest.mark.network
def test_bad_version():
    wl = WheelLocator("pynsist==0.99.99", "3.5.1", 64)
    with pytest.raises(NoWheelError):
        wl.get_from_pypi()

def test_extra_sources(tmpdir):
    src1 = Path(tmpdir, 'src1')
    src1.mkdir()
    src2 = Path(tmpdir, 'src2')
    src2.mkdir()

    # First one found wins, even if a later one is more specific.
    expected = (src1 / 'astsearch-0.1.2-py3-none-any.whl')
    expected.touch()
    (src2 / 'astsearch-0.1.2-py3-none-win_amd64.whl').touch()
    wl = WheelLocator("astsearch==0.1.2", "3.5.1", 64,
                      extra_sources=[src1, src2])
    assert wl.check_extra_sources() == expected

    wl = WheelLocator("astsearch==0.2.0", "3.5.1", 64,
                      extra_sources=[src1, src2])
    assert wl.check_extra_sources() is None

def test_pick_best_wheel():
    wd = WheelLocator("astsearch==0.1.2", "3.5.1", 64)

    # Some of the wheel filenames below are impossible combinations - they are
    # there to test the scoring and ranking machinery.

    # Prefer Windows-specific wheel
    releases = [
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-win_amd64.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[1]

    # Wrong Windows bitness
    releases = [
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-win_32.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[0]

    # Prefer more specific Python version
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[0]

    # Prefer more specific Python version
    releases = [
        CachedRelease('astsearch-0.1.2-py34.py35-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[0]

    # Incompatible Python version
    releases = [
        CachedRelease('astsearch-0.1.2-cp33-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[1]

    # Prefer more specific ABI version
    releases = [
        CachedRelease('astsearch-0.1.2-py3-abi3-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[0]

    # Incompatible ABI version
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-abi4-win_amd64.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[1]

    # Platform has priority over other attributes
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-abi3-any.whl'),
        CachedRelease('astsearch-0.1.2-py2.py3-none-win_amd64.whl'),
    ]
    assert wd.pick_best_wheel(releases) == releases[1]

def test_merge_dir_to(tmpdir_factory):
    td1 = tmpdir_factory.mktemp('td1')
    td2 = tmpdir_factory.mktemp('td2')

    td1 = Path(td1)
    td2 = Path(td2)

    with (td1 / 'ab').open('w') as f:
        f.write(u"original")
    with (td2 / 'ab').open('w') as f:
        f.write(u"alternate")

    (td1 / 'subdir').mkdir()
    with (td1 / 'subdir' / 'foo').open('w'): pass
    (td2 / 'subdir').mkdir()
    with (td2 / 'subdir' / 'bar').open('w'): pass

    merge_dir_to(td2, td1)

    assert_is_file(str(td1 / 'subdir' / 'foo'))
    assert_is_file(str(td1 / 'subdir' / 'bar'))
    with (td1 / 'ab').open() as f:
        assert f.read() == u"alternate"

    # Test with conflicts
    (td1 / 'conflict').mkdir()
    with (td2 / 'conflict').open('w'):
        pass

    with pytest.raises(RuntimeError):
        merge_dir_to(td2, td1)
    with pytest.raises(RuntimeError):
        merge_dir_to(td1, td2)
