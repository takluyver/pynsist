from nose.tools import *
from os.path import join as pjoin
from testpath import assert_isfile, assert_isdir
from testpath.tempdir import TemporaryDirectory

from nsist.pypi import WheelDownloader, extract_wheel, CachedRelease

def test_download():
    wd = WheelDownloader("astsearch==0.1.2", "3.5.1", 64)
    wheel = wd.fetch()
    assert_isfile(wheel)

    with TemporaryDirectory() as td:
        extract_wheel(wheel, target_dir=td)
        assert_isfile(pjoin(td, 'astsearch.py'))

# To exclude this, run:  nosetests -a '!network'
test_download.network = 1

def test_pick_best_wheel():
    wd = WheelDownloader("astsearch==0.1.2", "3.5.1", 64)

    # Some of the wheel filenames below are impossible combinations - they are
    # there to test the scoring and ranking machinery.

    # Prefer Windows-specific wheel
    releases = [
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-win_amd64.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[1])

    # Wrong Windows bitness
    releases = [
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-win_32.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[0])

    # Prefer more specific Python version
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[0])

    # Prefer more specific Python version
    releases = [
        CachedRelease('astsearch-0.1.2-py34.py35-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[0])

    # Incompatible Python version
    releases = [
        CachedRelease('astsearch-0.1.2-cp33-none-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[1])

    # Prefer more specific ABI version
    releases = [
        CachedRelease('astsearch-0.1.2-py3-abi3-any.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[0])

    # Incompatible ABI version
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-abi4-win_amd64.whl'),
        CachedRelease('astsearch-0.1.2-py3-none-any.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[1])

    # Platform has priority over other attributes
    releases = [
        CachedRelease('astsearch-0.1.2-cp35-abi3-any.whl'),
        CachedRelease('astsearch-0.1.2-py2.py3-none-win_amd64.whl'),
    ]
    assert_equal(wd.pick_best_wheel(releases), releases[1])
