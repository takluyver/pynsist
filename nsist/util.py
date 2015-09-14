import os
import errno
from pathlib import Path
import requests
import sys

PY3 = sys.version_info[0] >= 3

if PY3:
    text_types = (str,)
else:
    text_types = (str, unicode) # analysis:ignore


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

def get_cache_dir(ensure_existence=False):
    if os.name == 'posix' and sys.platform != 'darwin':
        # Linux, Unix, AIX, etc.
        # use ~/.cache if empty OR not set
        xdg = os.environ.get("XDG_CACHE_HOME", None) or (os.path.expanduser('~/.cache'))
        p = Path(xdg, 'pynsist')

    elif sys.platform == 'darwin':
        p = Path(os.path.expanduser('~'), 'Library/Caches/pynsist')

    else:
        # Windows (hopefully)
        local = os.environ.get('LOCALAPPDATA', None) or (os.path.expanduser('~\\AppData\\Local'))
        p = Path(local, 'pynsist')

    if ensure_existence:
        try:
            p.mkdir(parents=True)
        except OSError as e:
            # Py2 compatible equivalent of FileExistsError
            if e.errno != errno.EEXIST:
                raise

    return p
