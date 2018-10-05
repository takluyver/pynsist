import os
import logging
from pathlib import Path
import requests
import sys

logger = logging.getLogger(__name__)


def download(url, target):
    """Download a file using requests.
    
    This is like urllib.request.urlretrieve, but requests validates SSL
    certificates by default.
    """
    if isinstance(target, Path):
        target = str(target)

    from . import __version__
    headers = {'user-agent': 'Pynsist/'+__version__}
    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()
    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)

CACHE_ENV_VAR = 'PYNSIST_CACHE_DIR'

def get_cache_dir(ensure_existence=False):
    specified = os.environ.get(CACHE_ENV_VAR, None)

    if specified:
        p = Path(specified)
    elif os.name == 'posix' and sys.platform != 'darwin':
        # Linux, Unix, AIX, etc.
        # use ~/.cache if empty OR not set
        xdg = os.environ.get("XDG_CACHE_HOME", None) or (os.path.expanduser('~/.cache'))
        p = Path(xdg, 'pynsist')

    elif sys.platform == 'darwin':
        p = Path(os.path.expanduser('~'), 'Library/Caches/pynsist')

    else:
        # Windows (hopefully)
        local = os.environ.get('LOCALAPPDATA', None) or (os.path.expanduser('~\\AppData\\Local'))
        if local.startswith('~'):
            logger.warning("Could not find cache directory. Please set any of "
                           "these environment variables: "
                           "LOCALAPPDATA, HOME, USERPROFILE or HOMEPATH")
        p = Path(local, 'pynsist')

    if ensure_existence:
        p.mkdir(parents=True, exist_ok=True)

    return p


def normalize_path(path):
    """Normalize paths to contain "/" only"""
    return os.path.normpath(path).replace('\\', '/')
