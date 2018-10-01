"""Find, download and unpack wheels."""
import fnmatch
import hashlib
import logging
import glob
import os
import re
import shutil
import yarg
import zipfile

from pathlib import Path
from requests_download import download, HashTracker
from tempfile import mkdtemp

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
            name=re.sub(r'[^\w\d.]+', '_', self.name),
            version=re.sub(r'[^\w\d.]+', '_', self.version),
        )
        for source in self.extra_sources:
            candidates = [CachedRelease(p.name)
                          for p in source.iterdir()
                          if p.name.startswith(whl_filename_prefix)]
            rel = self.pick_best_wheel(candidates)
            if rel:
                path = source / rel.filename
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
            logger.info('Using wheel from extra directory: %s', p)
            return p

        p = self.check_cache()
        if p is not None:
            logger.info('Using cached wheel: %s', p)
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
    distributions = []
    # We try to get the wheels from wheels_pypi requirements parameter
    for req in wheels_requirements:
        wl = WheelLocator(req, py_version, bitness, extra_sources)
        whl_file = wl.fetch() 
        extract_wheel(whl_file, target_dir, exclude=exclude)
        distributions.append(wl.name)
    # Then from the local_wheels paths parameter
    for glob_path in wheels_paths:
        paths = glob.glob(glob_path)
        if not paths:
            raise ValueError('Error, glob path {0} does not match any wheel file'.format(glob_path))
        for path in glob.glob(glob_path):
            logger.info('Collecting wheel file: %s (from: %s)', os.path.basename(path), glob_path)
            validate_wheel(path, distributions, py_version, bitness)
            extract_wheel(path, target_dir, exclude=exclude)


def extract_distribution_and_version(wheel_name):
    """Extract distribution and version from a wheel file name"""
    search = re.search(r'^([^-]+)-([^-]+)-.*\.whl$', wheel_name)
    if not search:
        raise ValueError('Invalid wheel file name: {0}'.format(wheel_name))

    return (search.group(1), search.group(2))


def validate_wheel(whl_path, distributions, py_version, bitness):
    """
    Verify that the given wheel can safely be included in the current installer.
    If so, the given wheel info will be included in the given wheel info array.
    If not, an exception will be raised.
    """
    wheel_name = os.path.basename(whl_path)
    (distribution, version) = extract_distribution_and_version(wheel_name)

    # Check that a distribution of same name has not been included before
    if distribution in distributions:
        raise ValueError('Error, wheel distribution {0} already included'.format(distribution))

    # Check that the wheel is compatible with the installer environment
    locator = WheelLocator('{0}=={1}'.format(distribution, version), py_version, bitness, [Path(os.path.dirname(whl_path))])
    if not locator.check_extra_sources():
        raise ValueError('Error, wheel {0} is not compatible with Python {1} for Windows'.format(wheel_name, py_version))

    distributions.append(distribution)


def is_excluded(path, exclude):
    """Return True if path matches an exclude pattern"""
    path = normalize_path(path)
    for pattern in (exclude or ()):
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
