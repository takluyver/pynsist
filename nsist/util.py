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
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)