"""Build NSIS installers for Python applications.
"""
import errno
import logging
import os
import shutil
from subprocess import check_output, call
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve

if os.name == 'nt' and PY2:
    import _winreg as winreg
elif os.name == 'nt':
    import winreg
else:
    winreg = None

from .copymodules import copy_modules
from .nsiswriter import NSISFileWriter

__version__ = '0.2'

pjoin = os.path.join
logger = logging.getLogger(__name__)

_PKGDIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PY_VERSION = '2.7.6' if PY2 else '3.4.0'
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
    except OSError:
        logger.warn("GPG not available - could not check signature of {0}".format(target))



def fetch_pylauncher(bitness=DEFAULT_BITNESS, destination=DEFAULT_BUILD_DIR):
    """Fetch the MSI for PyLauncher (required for Python2.x).

    It will be placed in the destination directory.
    """
    arch_tag = '.amd64' if (bitness == 64) else ''
    url = ("https://bitbucket.org/vinay.sajip/pylauncher/downloads/"
           "launchwin{0}.msi".format(arch_tag))
    target = pjoin(destination, 'launchwin{0}.msi'.format(arch_tag))
    if os.path.isfile(target):
        logger.info('PyLauncher MSI already in build directory.')
        return
    logger.info('Downloading PyLauncher MSI...')
    urlretrieve(url, target)

SCRIPT_TEMPLATE = """#!python{qualifier}
import sys, os
scriptdir, script = os.path.split(__file__)
pkgdir = os.path.join(scriptdir, 'pkgs')
sys.path.insert(0, pkgdir)
os.environ['PYTHONPATH'] = pkgdir + os.pathsep + os.environ.get('PYTHONPATH', '')

def excepthook(etype, value, tb):
    "Write unhandled exceptions to a file rather than exiting silently."
    import traceback
    with open(os.path.join(scriptdir, script+'.log'), 'w') as f:
        traceback.print_exception(etype, value, tb, file=f)
sys.excepthook = excepthook

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

def prepare_shortcuts(shortcuts, py_version, py_bitness, build_dir):
    files = set()
    for scname, sc in shortcuts.items():
        if sc.get('entry_point'):
            sc['script'] = script = scname.replace(' ', '_') + '.launch.py'
            write_script(sc['entry_point'], py_version, py_bitness,
                            pjoin(build_dir, script))
        else:
            shutil.copy2(sc['script'], build_dir)
    
        shutil.copy2(sc['icon'], build_dir)
        sc['icon'] = os.path.basename(sc['icon'])
        sc['script'] = os.path.basename(sc['script'])
        files.add(sc['script'])
        files.add(sc['icon'])
    
    return files

def copy_extra_files(filelist, build_dir):
    """Copy a list of files into the build directory.
    
    Returns two lists, files and directories, with only the base filenames
    (i.e. no leading path components)
    """
    files, directories = [], []
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
            directories.append(basename)
        else:
            shutil.copy2(file, build_dir)
            files.append(basename)

    return files, directories

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
    except OSError as e:
        # This should catch either the registry key or makensis being absent
        if e.errno == errno.ENOENT:
            print("makensis was not found. Install NSIS and try again.")
            print("http://nsis.sourceforge.net/Download")
            return 1

def all_steps(appname, version, shortcuts, icon=DEFAULT_ICON, 
                packages=None, extra_files=None, py_version=DEFAULT_PY_VERSION,
                py_bitness=DEFAULT_BITNESS, build_dir=DEFAULT_BUILD_DIR,
                installer_name=None, nsi_template=DEFAULT_NSI_TEMPLATE):
    """Run all the steps to build an installer.
    
    For details of the parameters, see the documentation for the config file
    options.
    """
    installer_name = installer_name or make_installer_name(appname, version)

    try:
        os.makedirs(build_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
    fetch_python(version=py_version, bitness=py_bitness, destination=build_dir)
    if PY2:
        fetch_pylauncher(bitness=py_bitness, destination=build_dir)
    
    shortcuts_files = prepare_shortcuts(shortcuts, py_version, py_bitness, build_dir)
    
    # Packages
    logger.info("Copying packages into build directory...")
    build_pkg_dir = pjoin(build_dir, 'pkgs')
    if os.path.isdir(build_pkg_dir):
        shutil.rmtree(build_pkg_dir)
    if os.path.isdir('pynsist_pkgs'):
        shutil.copytree('pynsist_pkgs', build_pkg_dir)
    else:
        os.mkdir(build_pkg_dir)
    copy_modules(packages or [], build_pkg_dir, py_version=py_version)

    nsis_writer = NSISFileWriter(nsi_template,
        definitions = {'PRODUCT_NAME': appname,
                       'PRODUCT_VERSION': version,
                       'PY_VERSION': py_version,
                       'PRODUCT_ICON': os.path.basename(icon),
                       'INSTALLER_NAME': installer_name,
                       'ARCH_TAG': '.amd64' if (py_bitness==64) else '',
                      }
        )
    # Extra files
    nsis_writer.files, nsis_writer.directories = \
                            copy_extra_files(extra_files or [], build_dir)

    nsis_writer.files.extend(shortcuts_files)
    nsis_writer.shortcuts = shortcuts
    
    nsi_file = pjoin(build_dir, 'installer.nsi')
    nsis_writer.write(nsi_file)

    exitcode = run_nsis(nsi_file)
    
    if not exitcode:
        logger.info('Installer written to %s', pjoin(build_dir, installer_name))

def read_shortcuts_config(cfg):
    
    shortcuts = {}
    def _check_shortcut(name, sc, section):
        if ('entry_point' not in sc) and ('script' not in sc):
            raise ValueError('Section {} has neither entry_point nor script.'.format(section))
        elif ('entry_point' in sc) and ('script' in sc):
            raise ValueError('Section {} has both entry_point and script.'.format(section))
            
        # Copy to a regular dict so it can hold a boolean value
        sc2 = dict(sc)
        if 'icon' not in sc2:
            sc2['icon'] = DEFAULT_ICON        
        sc2['console'] = sc.getboolean('console', fallback=False)
        shortcuts[name] = sc2
    
    for section in cfg.sections():
        if section.startswith("Shortcut "):
            name = section[len("Shortcut "):]
            _check_shortcut(name, cfg[section], section)
    
    appcfg = cfg['Application']
    _check_shortcut(appcfg['name'], appcfg, 'Application')
    
    return shortcuts

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
    
    try:
        from . import configreader
        cfg = configreader.read_and_validate(config_file)
    except configreader.InvalidConfig as e:
        logger.error('Error parsing configuration file:')
        logger.error(str(e))
        sys.exit(1)
    appcfg = cfg['Application']
    all_steps(
        appname = appcfg['name'],
        version = appcfg['version'],
        icon = appcfg.get('icon', DEFAULT_ICON),
        shortcuts = read_shortcuts_config(cfg),
        packages = cfg.get('Include', 'packages', fallback='').splitlines(),
        extra_files = cfg.get('Include', 'files', fallback='').splitlines(),
        py_version = cfg.get('Python', 'version', fallback=DEFAULT_PY_VERSION),
        py_bitness = cfg.getint('Python', 'bitness', fallback=DEFAULT_BITNESS),
        build_dir = cfg.get('Build', 'directory', fallback=DEFAULT_BUILD_DIR),
        installer_name = cfg.get('Build', 'installer_name', fallback=None),
        nsi_template = cfg.get('Build', 'nsi_template', fallback=DEFAULT_NSI_TEMPLATE),
    )
