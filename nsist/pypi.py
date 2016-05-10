from distutils.version import LooseVersion
import errno
import hashlib
import logging
import re
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
            raise ValueError("Requirement {!r} did not match name==version")
        self.name, self.version = requirement.split('==', 1)

    def score_platform(self, platform):
        target = 'win_amd64' if self.bitness == 64 else 'win32'
        d = {target: 2, 'any': 1}
        return max(d.get(p, 0) for p in platform.split('.'))

    def score_abi(self, abi):
        # Are there other valid options here?
        d = {'abi3': 2, 'none': 1}
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
        dist_dir = get_cache_dir() / 'pypi' / self.name
        if not dist_dir.is_dir():
            return None

        if self.version:
            release_dir = dist_dir / self.version
        else:
            versions = [p.name for p in dist_dir.iterdir()]
            if not versions:
                return None
            latest = max(versions, key=LooseVersion)
            release_dir = dist_dir / latest

        rel = self.pick_best_wheel(CachedRelease(p.name)
                                   for p in release_dir.iterdir())
        if rel is None:
            return None
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

def extract_wheel(whl_file, target_dir):
    with zipfile.ZipFile(str(whl_file), mode='r') as zf:
        names = zf.namelist()
        # TODO: Do anything with data and dist-info folders?
        pkg_files = [n for n in names \
                     if not n.split('/')[0].endswith(('.data', '.dist-info'))]
        zf.extractall(target_dir, members=pkg_files)

def fetch_pypi_wheels(requirements, target_dir, py_version, bitness):
    for req in requirements:
        wd = WheelDownloader(req, py_version, bitness)
        whl_file = wd.fetch()
        extract_wheel(whl_file, target_dir)
