import os
import shutil
from subprocess import check_output, call
from urllib.request import urlretrieve

from .copymodules import copy_modules

pjoin = os.path.join

_PKGDIR = os.path.dirname(__file__)
DEFAULT_PY_VERSION = '3.3.2'
DEFAULT_BUILD_DIR = pjoin('build', 'nsis')
DEFAULT_ICON = pjoin(_PKGDIR, 'glossyorb.ico')
DEFAULT_INSTALLER_NAME = 'pynsis_installer.exe'

def fetch_python(version=DEFAULT_PY_VERSION, destination=DEFAULT_BUILD_DIR):
    """Fetch the MSI for the specified version of Python.
    
    It will be placed in the destination directory, and validated using GPG
    if possible.
    """
    url = 'http://python.org/ftp/python/{0}/python-{0}.msi'.format(version)
    target = pjoin(destination, 'python-{0}.msi'.format(version))
    if os.path.isfile(target):
        return
    urlretrieve(url, target)
    urlretrieve(url+'.asc', target+'.asc')
    try:
        keys_file = os.path.join(_PKGDIR, 'python-pubkeys.txt')
        check_output(['gpg', '--import', keys_file])
        check_output(['gpg', '--verify', target+'.asc'])
    except FileNotFoundError:
        print("GPG not available - could not check signature of {0}".format(target))

def write_nsis_file(nsi_file, definitions):
    with open(nsi_file, 'w') as f:
        for name, value in definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))
        
        with open(pjoin(_PKGDIR, 'template.nsi')) as f2:
            f.write(f2.read())

def run_nsis(nsi_file):
    call(['makensis', nsi_file])

def all_steps(appname, version, script, packages=None, icon=DEFAULT_ICON,
                py_version=DEFAULT_PY_VERSION, build_dir=DEFAULT_BUILD_DIR,
                installer_name=DEFAULT_INSTALLER_NAME):
    os.makedirs(build_dir, exist_ok=True)
    fetch_python(destination=build_dir)
    shutil.copy2(script, build_dir)
    shutil.copy2(icon, build_dir)
    build_pkg_dir = pjoin(build_dir, 'pkgs')
    if os.path.isdir('pynsis_pkgs'):
        shutil.copytree('pynsis_pkgs', build_pkg_dir)
    else:
        os.mkdir(build_pkg_dir)
    copy_modules(packages or [], build_pkg_dir)
    nsi_file = pjoin(build_dir, 'installer.nsi')
    definitions = {'PRODUCT_NAME': appname,
                   'PRODUCT_VERSION': version,
                   'PY_VERSION': py_version,
                   'SCRIPT': os.path.basename(script),
                   'PRODUCT_ICON': os.path.basename(icon),
                   'INSTALLER_NAME': installer_name,
                  }
    write_nsis_file(nsi_file, definitions)
    run_nsis(nsi_file)