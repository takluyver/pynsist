from distutils.version import LooseVersion
import errno
import hashlib
import logging
from pathlib import Path
import re
import shutil
from tempfile import mkdtemp
import zipfile

import yarg
from requests_download import download, HashTracker

from .util import get_cache_dir

logger = logging.getLogger(__name__)

def find_pypi_release(requirement):
    if '==' in requirement:
        name, version = requirement.split('==', 1)
        return yarg.get(name).release(version)
    else:
        return yarg.get(requirement).latest_release

class NoWheelError(Exception): pass

class WheelDownloader(object):
    def __init__(self, requirement, py_version, bitness):
        self.requirement = requirement
        self.py_version = py_version
        self.bitness = bitness

        if requirement.count('==') != 1:
            raise ValueError("Requirement {!r} did not match name==version".format(requirement))
        self.name, self.version = requirement.split('==', 1)

    def score_platform(self, platform):
        target = 'win_amd64' if self.bitness == 64 else 'win32'
        d = {target: 2, 'any': 1}
        return max(d.get(p, 0) for p in platform.split('.'))

    def score_abi(self, abi):
        py_version_nodot = ''.join(self.py_version.split('.')[:2])
        # Are there other valid options here?
        d = {'cp%sm' % py_version_nodot: 3,  # Is the m reliable?
            'abi3': 2, 'none': 1}
        return max(d.get(a, 0) for a in abi.split('.'))

    def score_interpreter(self, interpreter):
        py_version_nodot = ''.join(self.py_version.split('.')[:2])
        py_version_major = self.py_version.split('.')[0]
        d = {'cp'+py_version_nodot: 4,
             'cp'+py_version_major: 3,
             'py'+py_version_nodot: 2,
             'py'+py_version_major: 1
            }
        return max(d.get(i, 0) for i in interpreter.split('.'))

    def pick_best_wheel(self, release_list):
        best_score = (0, 0, 0)
        best = None
        for release in release_list:
            if release.package_type != 'wheel':
                continue

            m = re.search(r'-([^-]+)-([^-]+)-([^-]+)\.whl', release.filename)
            if not m:
                continue

            interpreter, abi, platform = m.group(1, 2, 3)
            score = (self.score_platform(platform),
                     self.score_abi(abi),
                     self.score_interpreter(interpreter)
                    )
            if any(s==0 for s in score):
                # Incompatible
                continue

            if score > best_score:
                best = release
                best_score = score

        return best

    def check_cache(self):
        release_dir = get_cache_dir() / 'pypi' / self.name / self.version
        if not release_dir.is_dir():
            return None

        rel = self.pick_best_wheel(CachedRelease(p.name)
                                   for p in release_dir.iterdir())
        if rel is None:
            return None

        logger.info('Using cached wheel: %s', rel.filename)
        return release_dir / rel.filename

    def fetch(self):
        p = self.check_cache()
        if p is not None:
            return p

        release_list = yarg.get(self.name).release(self.version)
        preferred_release = self.pick_best_wheel(release_list)
        if preferred_release is None:
            raise NoWheelError('No compatible wheels found for {0.name} {0.version}'.format(self))

        download_to = get_cache_dir() / 'pypi' / self.name / self.version
        try:
            download_to.mkdir(parents=True)
        except OSError as e:
            # Py2 compatible equivalent of FileExistsError
            if e.errno != errno.EEXIST:
                raise
        target = download_to / preferred_release.filename

        from . import __version__
        hasher = HashTracker(hashlib.md5())
        headers = {'user-agent': 'pynsist/'+__version__}
        logger.info('Downloading wheel: %s', preferred_release.url)
        download(preferred_release.url, str(target), headers=headers,
                 trackers=(hasher,))
        if hasher.hashobj.hexdigest() != preferred_release.md5_digest:
            target.unlink()
            raise ValueError('Downloaded wheel corrupted: {}'.format(preferred_release.url))

        return target


class CachedRelease(object):
    # Mock enough of the yarg Release object to be compatible with
    # pick_best_release above
    def __init__(self, filename):
        self.filename = filename
        self.package_type = 'wheel' if filename.endswith('.whl') else ''

def merge_dir_to(src, dst):
    """Merge all files from one directory into another.

    Subdirectories will be merged recursively. If filenames are the same, those
    from src will overwrite those in dst. If a regular file clashes with a
    directory, an error will occur.
    """
    for p in src.iterdir():
        if p.is_dir():
            dst_p = dst / p.name
            if dst_p.is_dir():
                merge_dir_to(p, dst_p)
            elif dst_p.is_file():
                raise RuntimeError('Directory {} clashes with file {}'
                                   .format(p, dst_p))
            else:
                shutil.copytree(str(p), str(dst_p))
        else:
            # Copy regular file
            dst_p = dst / p.name
            if dst_p.is_dir():
                raise RuntimeError('File {} clashes with directory {}'
                                   .format(p, dst_p))
            shutil.copy2(str(p), str(dst_p))

def extract_wheel(whl_file, target_dir):
    """Extract importable modules from a wheel to the target directory
    """
    # Extract to temporary directory
    td = Path(mkdtemp())
    with zipfile.ZipFile(str(whl_file), mode='r') as zf:
        zf.extractall(str(td))

    # Move extra lib files out of the .data subdirectory
    for p in td.iterdir():
        if p.suffix == '.data':
            if (p / 'purelib').is_dir():
                merge_dir_to(p / 'purelib', td)
            if (p / 'platlib').is_dir():
                merge_dir_to(p / 'platlib', td)

    # Copy to target directory
    target = Path(target_dir)
    copied_something = False
    for p in td.iterdir():
        if p.suffix not in {'.data', '.dist-info'}:
            if p.is_dir():
                # If the dst directory already exists, this will combine them.
                # shutil.copytree will not combine them.
                target.joinpath(p.name).mkdir(exist_ok = True)
                merge_dir_to(p, target / p.name)
            else:
                shutil.copy2(str(p), str(target))
            copied_something = True

    if not copied_something:
        raise RuntimeError("Did not find any files to extract from wheel {}"
                           .format(whl_file))

    # Clean up temporary directory
    shutil.rmtree(str(td))


def fetch_pypi_wheels(requirements, target_dir, py_version, bitness):
    for req in requirements:
        wd = WheelDownloader(req, py_version, bitness)
        whl_file = wd.fetch()
        extract_wheel(whl_file, target_dir)
