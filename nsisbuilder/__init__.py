import logging
import os
import shutil
from subprocess import check_output, call
from urllib.request import urlretrieve

from .copymodules import copy_modules

pjoin = os.path.join
logger = logging.getLogger(__name__)

_PKGDIR = os.path.dirname(__file__)
DEFAULT_PY_VERSION = '3.3.2'
DEFAULT_BUILD_DIR = pjoin('build', 'nsis')
DEFAULT_ICON = pjoin(_PKGDIR, 'glossyorb.ico')
DEFAULT_INSTALLER_NAME = 'pynsis_installer.exe'
if os.name == 'nt' and sys.maxsize == (2**63)-1:
    DEFAULT_BITNESS = 64
else:
    DEFAULT_BITNESS = 32

def fetch_python(version=DEFAULT_PY_VERSION, bitness=DEFAULT_BITNESS,
                 destination=DEFAULT_BUILD_DIR):
    """Fetch the MSI for the specified version of Python.
    
    It will be placed in the destination directory, and validated using GPG
    if possible.
    """
    arch_tag = '.amd64' if (bitness==64) else ''
    url = 'http://python.org/ftp/python/{0}/python-{0}{1}.msi'.format(version, arch_tag)
    target = pjoin(destination, 'python-{0}{1}.msi'.format(version, arch_tag))
    if os.path.isfile(target):
        logger.info('Python MSI already in build directory.')
        return
    logger.info('Downloading Python MSI...')
    urlretrieve(url, target)
    urlretrieve(url+'.asc', target+'.asc')
    try:
        keys_file = os.path.join(_PKGDIR, 'python-pubkeys.txt')
        check_output(['gpg', '--import', keys_file])
        check_output(['gpg', '--verify', target+'.asc'])
    except FileNotFoundError:
        logger.warn("GPG not available - could not check signature of {0}".format(target))

def copy_extra_files(filelist, files_dir):
    for file in filelist:
        file = file.rstrip('/\\')
        if os.path.isdir(file):
            target_name = pjoin(files_dir, os.path.basename(file))
            shutil.copytree(file, target_name)
        else:
            shutil.copy2(file, files_dir)

def write_nsis_file(nsi_file, definitions):
    with open(nsi_file, 'w') as f:
        for name, value in definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))
        
        with open(pjoin(_PKGDIR, 'template.nsi')) as f2:
            f.write(f2.read())

def run_nsis(nsi_file):
    call(['makensis', nsi_file])

def all_steps(appname, version, script, icon=DEFAULT_ICON, packages=None,
                extra_files=None, py_version=DEFAULT_PY_VERSION,
                py_bitness=DEFAULT_BITNESS, build_dir=DEFAULT_BUILD_DIR,
                installer_name=DEFAULT_INSTALLER_NAME):
    os.makedirs(build_dir, exist_ok=True)
    fetch_python(version=py_version, bitness=py_bitness, destination=build_dir)
    shutil.copy2(script, build_dir)
    shutil.copy2(icon, build_dir)
    
    # Packages
    build_pkg_dir = pjoin(build_dir, 'pkgs')
    if os.path.isdir(build_pkg_dir):
        shutil.rmtree(build_pkg_dir)
    if os.path.isdir('pynsis_pkgs'):
        shutil.copytree('pynsis_pkgs', build_pkg_dir)
    else:
        os.mkdir(build_pkg_dir)
    copy_modules(packages or [], build_pkg_dir)
    
    # Extra files
    files_dir = pjoin(build_dir, 'files')
    if os.path.isdir(files_dir):
        shutil.rmtree(files_dir)
    os.mkdir(files_dir)
    copy_extra_files(extra_files or [], files_dir)

    nsi_file = pjoin(build_dir, 'installer.nsi')
    definitions = {'PRODUCT_NAME': appname,
                   'PRODUCT_VERSION': version,
                   'PY_VERSION': py_version,
                   'SCRIPT': os.path.basename(script),
                   'PRODUCT_ICON': os.path.basename(icon),
                   'INSTALLER_NAME': installer_name,
                   'ARCH_TAG': '.amd64' if (py_bitness==64) else ''
                  }
    write_nsis_file(nsi_file, definitions)
    run_nsis(nsi_file)

def main(argv=None):
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    
    import argparse
    argp = argparse.ArgumentParser(prog='pynsis')
    argp.add_argument('config_file')
    options = argp.parse_args(argv)
    
    dirname, config_file = os.path.split(options.config_file)
    if dirname:
        os.chdir(dirname)
    
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    appcfg = cfg['Application']
    all_steps(
        appname = appcfg['name'],
        version = appcfg['version'],
        script = appcfg['script'],
        icon = appcfg.get('icon', DEFAULT_ICON),
        packages = cfg.get('Include', 'packages', fallback='').splitlines(),
        extra_files = cfg.get('Include', 'files', fallback='').splitlines(),
        py_version = cfg.get('Python', 'version', fallback=DEFAULT_PY_VERSION),
        py_bitness = cfg.getint('Python', 'bitness', fallback=DEFAULT_BITNESS),
        build_dir = cfg.get('Build', 'directory', fallback=DEFAULT_BUILD_DIR),
        installer_name = cfg.get('Build', 'installer_name', fallback=DEFAULT_INSTALLER_NAME),
    )
