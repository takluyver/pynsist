"""Find, download and unpack wheels."""
import fnmatch
import hashlib
import itertools
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

class CompatibilityScorer:
    """Score wheels for a given target platform

    0 for any score means incompatible.
    Higher numbers are more platform specific.
    """
    def __init__(self, py_version, platform):
        self.py_version = py_version
        py_version_tuple = tuple(map(int, py_version.split('.')[:2]))
        self.platform = platform
        # {('cp38', 'none', 'any'): N}  (higher N for more specific tags)
        self.tag_prio = {
            tag: i for i, tag in enumerate(reversed(
                list(compatible_tags(py_version_tuple, platform))
            ), start=1)
        }

    def score(self, whl_filename: str) -> int:
        """Return a number for how suitable a wheel is for the target Python

        Higher numbers mean more specific (preferred) tags. 0 -> incompatible.
        """
        m = re.search(r'-([^-]+)-([^-]+)-([^-]+)\.whl$', whl_filename)
        if not m:
            raise ValueError("Failed to find wheel tag in %r" % whl_filename)

        interpreter, abi, platform = m.group(1, 2, 3)
        # Expand compressed tags ('cp38.cp39' indicates compatibility w/ both)
        expanded_tags = itertools.product(
            interpreter.split('.'), abi.split('.'), platform.split('.')
        )
        return max(self.tag_prio.get(whl_tag, 0) for whl_tag in expanded_tags)

    def is_compatible(self, whl_filename: str) -> bool:
        return self.score(whl_filename) > 0

class WheelLocator(object):
    def __init__(self, requirement, scorer, extra_sources=None):
        self.requirement = requirement
        self.scorer = scorer
        self.extra_sources = extra_sources or []

        if requirement.count('==') != 1:
            raise ValueError("Requirement {!r} did not match name==version".format(requirement))
        self.name, self.version = requirement.split('==', 1)

    def pick_best_wheel(self, release_list):
        """Return the most specific compatible wheel

        Returns None if none of the supplied
        """
        best_score = 0
        best = None
        for release in release_list:
            if release.package_type != 'wheel':
                continue

            score = self.scorer.score(release.filename)
            if score == 0:
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
            exclude_regexen = make_exclude_regexen(exclude)
            for zpath in zf.namelist():
                if is_excluded('pkgs/' + zpath, exclude_regexen):
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

            # HACK: Some wheels from Christoph Gohlke's page have extra package
            # files added in data/Lib/site-packages. This is a trick that relies
            # on the default installation layout. It doesn't look like it will
            # change, so in the best tradition of packaging, we'll work around
            # the workaround.
            # https://github.com/takluyver/pynsist/issues/171
            # This is especially ugly because we do a case-insensitive match,
            # regardless of the filesystem.
            if (p / 'data').is_dir():
                for sd in (p / 'data').iterdir():
                    if sd.name.lower() == 'lib' and sd.is_dir():
                        for sd2 in sd.iterdir():
                            if sd2.name.lower() == 'site-packages' and sd2.is_dir():
                                merge_dir_to(sd2, td)

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

class WheelGetter:
    def __init__(self, requirements, wheel_globs, target_dir,
                 py_version, bitness, extra_sources=None, exclude=None):
        self.requirements = requirements
        self.wheel_globs = wheel_globs
        self.target_dir = target_dir
        target_platform = 'win_amd64' if bitness == 64 else 'win32'
        self.scorer = CompatibilityScorer(py_version, target_platform)
        self.extra_sources = extra_sources
        self.exclude = exclude

        self.got_distributions = {}

    def get_all(self):
        self.get_requirements()
        self.get_globs()

    def get_requirements(self):
        for req in self.requirements:
            wl = WheelLocator(req, self.scorer, self.extra_sources)
            whl_file = wl.fetch()
            extract_wheel(whl_file, self.target_dir, exclude=self.exclude)
            self.got_distributions[wl.name] = whl_file

    def get_globs(self):
        for glob_path in self.wheel_globs:
            paths = glob.glob(glob_path)
            if not paths:
                raise ValueError('Glob path {} does not match any files'
                                 .format(glob_path))
            for path in paths:
                logger.info('Collecting wheel file: %s (from: %s)',
                            os.path.basename(path), glob_path)
                self.validate_wheel(path)
                extract_wheel(path, self.target_dir, exclude=self.exclude)

    def validate_wheel(self, whl_path):
        """
        Verify that the given wheel can safely be included in the current installer.
        If so, the given wheel info will be included in the given wheel info array.
        If not, an exception will be raised.
        """
        wheel_name = os.path.basename(whl_path)
        distribution = wheel_name.split('-', 1)[0]

        # Check that a distribution of same name has not been included before
        if distribution in self.got_distributions:
            prev_path = self.got_distributions[distribution]
            raise ValueError('Multiple wheels specified for {}:\n  {}\n  {}'.format(
                             distribution, prev_path, whl_path))

        # Check that the wheel is compatible with the installer environment
        if not self.scorer.is_compatible(wheel_name):
            raise ValueError('Wheel {} is not compatible with Python {}, {}'
                .format(wheel_name, self.scorer.py_version, self.scorer.platform))

        self.got_distributions[distribution] = whl_path


def make_exclude_regexen(exclude_patterns):
    """Translate exclude glob patterns to regex pattern objects.

    Handles matching files under a named directory.
    """
    re_pats = set()
    for pattern in exclude_patterns:
        re_pats.add(fnmatch.translate(pattern))
        if not pattern.endswith('*'):
            # Also use the pattern as a directory name and match anything
            # under that directory.
            suffix = '*' if pattern.endswith('/') else '/*'
            re_pats.add(fnmatch.translate(pattern + suffix))

    return [re.compile(p) for p in sorted(re_pats)]


def is_excluded(path, exclude_regexen):
    """Return True if path matches an exclude pattern"""
    path = normalize_path(path)
    for re_pattern in exclude_regexen:
        if re_pattern.match(path):
            return True
    return False

# The function below is based on the packaging.tags module, used with
# modification following the BSD 2 clause license:

# Copyright (c) Donald Stufft and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def compatible_tags(python_version : tuple =None, platform : str =None):
    """Iterate through compatible tags for our target Python

    Tags are yielded in order from the most specific to the most general.

    Based on packaging.tags module, but simplified for Pynsist's use case,
    and avoiding getting any details from the currently running Python.
    """
    interpreter = "cp{}{}".format(python_version[0], python_version[1])

    cpython_abi = interpreter
    # Python is normally built with the pymalloc (m) option, and most wheels
    # are published for this ABI. The flag is dropped in Python 3.8.
    if python_version < (3, 8):
        cpython_abi += 'm'

    yield interpreter, cpython_abi, platform
    yield interpreter, "abi3", platform
    yield interpreter, "none", platform

    # cp3x-abi3 down to cp32 (Python 3.2 was the first version to have ABI3)
    for minor_version in range(python_version[1] - 1, 1, -1):
        interpreter = "cp{}{}".format(python_version[0], minor_version)
        yield interpreter, "abi3", platform

    py_interps = [
        f"py{python_version[0]}{python_version[1]}",  # e.g. py38
        f"py{python_version[0]}",                     # py3
    ] + [
        f"py{python_version[0]}{minor}"               # py37 ... py30
        for minor in range(python_version[1] - 1, -1, -1)
    ]

    for version in py_interps:
        yield version, "none", platform
    for version in py_interps:
        yield version, "none", "any"
