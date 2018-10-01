"""Find, download and unpack wheels."""
import fnmatch
import hashlib
import logging
from pathlib import Path
import re
import shutil
from tempfile import mkdtemp
import zipfile
import glob
import os

import yarg
from requests_download import download, HashTracker

from .util import get_cache_dir, normalize_path

logger = logging.getLogger(__name__)

class NoWheelError(Exception): pass

class WheelLocator(object):
    def __init__(self, requirement, py_version, bitness, extra_sources=None):
        self.requirement = requirement
        self.py_version = py_version
        self.bitness = bitness
        self.extra_sources = extra_sources or []

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

    def check_extra_sources(self):
        """Find a compatible wheel in the specified extra_sources directories.

        Returns a Path or None.
        """
        whl_filename_prefix = '{name}-{version}-'.format(
            name=re.sub("[^\w\d.]+", "_", self.name),
            version=re.sub("[^\w\d.]+", "_", self.version),
        )
        for source in self.extra_sources:
            candidates = [CachedRelease(p.name)
                          for p in source.iterdir()
                          if p.name.startswith(whl_filename_prefix)]
            rel = self.pick_best_wheel(candidates)
            if rel:
                path = source / rel.filename
                logger.info('Using wheel from extra directory: %s', path)
                return path

    def check_cache(self):
        """Find a wheel previously downloaded from PyPI in the cache.

        Returns a Path or None.
        """
        release_dir = get_cache_dir() / 'pypi' / self.name / self.version
        if not release_dir.is_dir():
            return None

        rel = self.pick_best_wheel(CachedRelease(p.name)
                                   for p in release_dir.iterdir())
        if rel is None:
            return None

        logger.info('Using cached wheel: %s', rel.filename)
        return release_dir / rel.filename

    def get_from_pypi(self):
        """Download a compatible wheel from PyPI.

        Downloads to the cache directory and returns the destination as a Path.
        Raises NoWheelError if no compatible wheel is found.
        """
        try:
            pypi_pkg = yarg.get(self.name)
        except yarg.HTTPError as e:
            if e.status_code == 404:
                raise NoWheelError("No package named {} found on PyPI".format(self.name))
            raise

        release_list = pypi_pkg.release(self.version)
        if release_list is None:
            raise NoWheelError("No release {0.version} for package {0.name}".format(self))

        preferred_release = self.pick_best_wheel(release_list)
        if preferred_release is None:
            raise NoWheelError('No compatible wheels found for {0.name} {0.version}'.format(self))

        download_to = get_cache_dir() / 'pypi' / self.name / self.version
        try:
            download_to.mkdir(parents=True)
        except OSError:
            # Ignore OSError only if the directory exists
            if not download_to.is_dir():
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

    def fetch(self):
        """Find and return a compatible wheel (main interface)"""
        p = self.check_extra_sources()
        if p is not None:
            return p

        p = self.check_cache()
        if p is not None:
            return p

        return self.get_from_pypi()


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


def extract_wheel(whl_file, target_dir, exclude=None):
    """Extract importable modules from a wheel to the target directory
    """
    # Extract to temporary directory
    td = Path(mkdtemp())
    with zipfile.ZipFile(str(whl_file), mode='r') as zf:
        if exclude:
            basename = Path(Path(target_dir).name)
            for zpath in zf.namelist():
                path = basename / zpath
                if is_excluded(path, exclude):
                    continue  # Skip excluded paths
                zf.extract(zpath, path=str(td))
        else:
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
        if p.suffix not in {'.data'}:
            if p.is_dir():
                # If the dst directory already exists, this will combine them.
                # shutil.copytree will not combine them.
                try:
                    target.joinpath(p.name).mkdir()
                except OSError:
                    if not target.joinpath(p.name).is_dir():
                        raise
                merge_dir_to(p, target / p.name)
            else:
                shutil.copy2(str(p), str(target))
            copied_something = True

    if not copied_something:
        raise RuntimeError("Did not find any files to extract from wheel {}"
                           .format(whl_file))

    # Clean up temporary directory
    shutil.rmtree(str(td))


def fetch_pypi_wheels(wheels_requirements, wheels_paths, target_dir, py_version,
                      bitness, extra_sources=None, exclude=None):
    """
    Gather wheels included explicitly by wheels_pypi parameter 
    or matching glob paths given in local_wheels parameter.
    """
    wheel_info_array = []
    # We try to get the wheels from wheels_pypi requirements parameter
    for req in wheels_requirements:
        wl = WheelLocator(req, py_version, bitness, extra_sources)
        whl_file = wl.fetch() 
        validate_wheel(whl_file, wheel_info_array, py_version)
        extract_wheel(whl_file, target_dir, exclude=exclude)
    # Then from the local_wheels paths parameter
    for glob_path in wheels_paths:
        for path in glob.glob(glob_path):
            logger.info('Include wheel: %s (local_wheels path: %s)', os.path.basename(path), glob_path)
            validate_wheel(path, wheel_info_array, py_version)
            extract_wheel(path, target_dir, exclude=exclude)


def validate_wheel(whl_path, wheel_info_array, py_version):
    """
    Verify that the given wheel can safely be included in the current installer.
    If so, the given wheel info will be included in the given wheel info array.
    If not, an exception will be raised.
    """
    wheel_info = info_from_wheel_path(whl_path)

    # Check that a distribution of same name has not been included before
    if wheel_info['distribution'] in [item['distribution'] for item in wheel_info_array]:
        raise ValueError('Error, wheel distribution {0} already included'.format(wheel_info['distribution']))

    # Check that the wheel is compatible with the included python version
    search_python_tag = re.search(r'^(\d+).(\d+)', py_version)
    accepted_python_tags = [
        'py{0}{1}'.format(search_python_tag.group(1), search_python_tag.group(2)), 
        'py{0}'.format(search_python_tag.group(1)),
        'cp{0}{1}'.format(search_python_tag.group(1), search_python_tag.group(2)), 
        'cp{0}'.format(search_python_tag.group(1))]
    if not set(accepted_python_tags) & set(wheel_info['python_tag'].split('.')):
        raise ValueError('Error, wheel {0} does not support Python {1}'.format(wheel_info['wheel_name'], py_version))

    # Check that the wheel is compatible with Windows platforms
    if wheel_info['platform_tag'] not in ['any', 'win32', 'win_x86_64']:
        raise ValueError('Error, wheel {0} does not support Windows platform'.format(wheel_info['wheel_name']))

    wheel_info_array.append(wheel_info)


def info_from_wheel_path(wheel_path):
    """Build and wheel object description from the given wheel path"""
    wheel_name = os.path.basename(wheel_path)
    search = re.search(r'^(.*)-(.*)(?:-(.*)|)-(.*)-(.*)-(.*)\.whl$', wheel_name)
    if not search:
        raise ValueError('Invalid wheel file name: {0}'.format(wheel_name))

    if search.group(6):
        return {
            'wheel_name': wheel_name,
            'distribution': search.group(1),
            'version': search.group(2),
            'build_tag': search.group(3),
            'python_tag': search.group(4),
            'abi_tag': search.group(5),
            'platform_tag': search.group(6),
        }
    else:
        return {
            'wheel_name': wheel_name,
            'distribution': search.group(1),
            'version': search.group(2),
            'build_tag': None,
            'python_tag': search.group(3),
            'abi_tag': search.group(4),
            'platform_tag': search.group(5),
        }


def is_excluded(path, exclude):
    """Return True if path matches an exclude pattern"""
    path = normalize_path(path)
    for pattern in (exclude or ()):
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
