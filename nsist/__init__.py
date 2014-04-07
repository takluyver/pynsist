"""Build NSIS installers for Python applications.
"""
import logging
import os
import shutil
from subprocess import check_output, call
import sys
from urllib.request import urlretrieve
if os.name == 'nt':
    import winreg
else:
    winreg = None

from .copymodules import copy_modules
from .nsiswriter import NSISFileWriter

pjoin = os.path.join
logger = logging.getLogger(__name__)

_PKGDIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PY_VERSION = '3.3.2'
DEFAULT_BUILD_DIR = pjoin('build', 'nsis')
DEFAULT_NSI_TEMPLATE = pjoin(_PKGDIR, 'template.nsi')
DEFAULT_ICON = pjoin(_PKGDIR, 'glossyorb.ico')
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

SCRIPT_TEMPLATE = """#!python{qualifier}
import sys
sys.path.insert(0, 'pkgs')
from {module} import {func}
{func}()
"""

def write_script(entrypt, python_version, bitness, target):
    """Write a launcher script from a 'module:function' entry point
    
    python_version and bitness are used to write an appropriate shebang line
    for the PEP 397 Windows launcher.
    """
    qualifier = '.'.join(python_version.split('.')[:2])
    if bitness == 32:
        qualifier += '-32'
    module, func = entrypt.split(":")
    with open(target, 'w') as f:
        f.write(SCRIPT_TEMPLATE.format(qualifier=qualifier, module=module, func=func))

def copy_extra_files(filelist, build_dir):
    """Copy a list of files into the build directory.
    
    Returns a list of 2-tuples: the filename without any path coomponents,
    and a boolean that is True if the file is a directory.
    """
    results = []  # name, is_directory
    for file in filelist:
        file = file.rstrip('/\\')
        basename = os.path.basename(file)
        if os.path.isdir(file):
            target_name = pjoin(build_dir, basename)
            if os.path.isdir(target_name):
                shutil.rmtree(target_name)
            elif os.path.exists(target_name):
                os.unlink(target_name)
            shutil.copytree(file, target_name)
            results.append((basename, True))
        else:
            shutil.copy2(file, build_dir)
            results.append((basename, False))
    return results

def make_installer_name(appname, version):
    """Generate the filename of the installer exe
    
    e.g. My_App_1.0.exe
    """
    s = appname + '_' + version + '.exe'
    return s.replace(' ', '_')

def run_nsis(nsi_file):
    """Runs makensis using the specified .nsi file
    
    Returns the exit code.
    """
    try:
        if os.name == 'nt':
            makensis = pjoin(winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\NSIS'),
                                     'makensis.exe')
        else:
            makensis = 'makensis'
        return call([makensis, nsi_file])
    except FileNotFoundError:
        # FileNotFoundError catches both the registry lookup failing and call()
        # not finding makensis
        print("makensis was not found. Install NSIS and try again.")
        print("http://nsis.sourceforge.net/Download")
        return 1

def all_steps(appname, version, script=None, entry_point=None, icon=DEFAULT_ICON, console=False,
                packages=None, extra_files=None, py_version=DEFAULT_PY_VERSION,
                py_bitness=DEFAULT_BITNESS, build_dir=DEFAULT_BUILD_DIR,
                installer_name=None, nsi_template=DEFAULT_NSI_TEMPLATE):
    """Run all the steps to build an installer.
    
    For details of the parameters, see the documentation for the config file
    options.
    """
    installer_name = installer_name or make_installer_name(appname, version)

    os.makedirs(build_dir, exist_ok=True)
    fetch_python(version=py_version, bitness=py_bitness, destination=build_dir)

    if entry_point is not None:
        if script is not None:
            raise ValueError('Both script and entry_point were specified.')
        script = 'launch.py'
        write_script(entry_point, py_version, py_bitness, pjoin(build_dir, script))
    elif script is not None:
        shutil.copy2(script, build_dir)
    else:
        raise ValueError('Neither script nor entry_point was specified.')

    shutil.copy2(icon, build_dir)
    
    # Packages
    logger.info("Copying packages into build directory...")
    build_pkg_dir = pjoin(build_dir, 'pkgs')
    if os.path.isdir(build_pkg_dir):
        shutil.rmtree(build_pkg_dir)
    if os.path.isdir('pynsist_pkgs'):
        shutil.copytree('pynsist_pkgs', build_pkg_dir)
    else:
        os.mkdir(build_pkg_dir)
    copy_modules(packages or [], build_pkg_dir)

    nsis_writer = NSISFileWriter(nsi_template,
        definitions = {'PRODUCT_NAME': appname,
                       'PRODUCT_VERSION': version,
                       'PY_VERSION': py_version,
                       'SCRIPT': os.path.basename(script),
                       'PRODUCT_ICON': os.path.basename(icon),
                       'INSTALLER_NAME': installer_name,
                       'ARCH_TAG': '.amd64' if (py_bitness==64) else '',
                       'PY_EXE': 'py' if console else 'pyw',
                      }
        )
    # Extra files
    nsis_writer.extra_files = copy_extra_files(extra_files or [], build_dir)

    nsi_file = pjoin(build_dir, 'installer.nsi')
    nsis_writer.write(nsi_file)

    exitcode = run_nsis(nsi_file)
    
    if not exitcode:
        logger.info('Installer written to %s', pjoin(build_dir, installer_name))

def main(argv=None):
    """Make an installer from the command line.
    
    This parses command line arguments and a config file, and calls
    :func:`all_steps` with the extracted information.
    """
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    
    import argparse
    argp = argparse.ArgumentParser(prog='pynsist')
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
        script = appcfg.get('script', fallback=None),
        entry_point = appcfg.get('entry_point', fallback=None),
        icon = appcfg.get('icon', DEFAULT_ICON),
        console = appcfg.getboolean('console', fallback=False),
        packages = cfg.get('Include', 'packages', fallback='').splitlines(),
        extra_files = cfg.get('Include', 'files', fallback='').splitlines(),
        py_version = cfg.get('Python', 'version', fallback=DEFAULT_PY_VERSION),
        py_bitness = cfg.getint('Python', 'bitness', fallback=DEFAULT_BITNESS),
        build_dir = cfg.get('Build', 'directory', fallback=DEFAULT_BUILD_DIR),
        installer_name = cfg.get('Build', 'installer_name', fallback=None),
        nsi_template = cfg.get('Build', 'nsi_template', fallback=DEFAULT_NSI_TEMPLATE),
    )
