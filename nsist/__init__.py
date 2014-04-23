"""Build NSIS installers for Python applications.
"""
import errno
import logging
import os
import shutil
from subprocess import call
import sys

PY2 = sys.version_info[0] == 2

if os.name == 'nt':
    if PY2:
        import _winreg as winreg
    else:
        import winreg
else:
    winreg = None

from .copymodules import copy_modules
from .nsiswriter import NSISFileWriter
from .util import download

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

class InstallerBuilder(object):
    def __init__(self, appname, version, shortcuts, icon=DEFAULT_ICON, 
                packages=None, extra_files=None, py_version=DEFAULT_PY_VERSION,
                py_bitness=DEFAULT_BITNESS, build_dir=DEFAULT_BUILD_DIR,
                installer_name=None, nsi_template=DEFAULT_NSI_TEMPLATE):
        self.appname = appname
        self.version = version
        self.shortcuts = shortcuts
        self.icon = icon
        self.packages = packages or []
        self.extra_files = extra_files or []
        self.py_version = py_version
        self.py_bitness = py_bitness
        self.build_dir = build_dir
        self.installer_name = installer_name or self.make_installer_name()
        self.nsi_template = nsi_template
        self.nsi_file = pjoin(self.build_dir, 'installer.nsi')
        self.py_qualifier = '.'.join(self.py_version.split('.')[:2])
        if self.py_bitness == 32:
            self.py_qualifier += '-32'
        
        # To be filled later
        self.install_files = []
        self.install_dirs = []
    
    def make_installer_name(self):
        """Generate the filename of the installer exe
        
        e.g. My_App_1.0.exe
        """
        s = self.appname + '_' + self.version + '.exe'
        return s.replace(' ', '_')

    def fetch_python(self):
        """Fetch the MSI for the specified version of Python.
        
        It will be placed in the destination directory, and validated using GPG
        if possible.
        """
        version = self.py_version
        arch_tag = '.amd64' if (self.py_bitness==64) else ''
        url = 'https://python.org/ftp/python/{0}/python-{0}{1}.msi'.format(version, arch_tag)
        target = pjoin(self.build_dir, 'python-{0}{1}.msi'.format(version, arch_tag))
        if os.path.isfile(target):
            logger.info('Python MSI already in build directory.')
            return
        logger.info('Downloading Python MSI...')
        download(url, target)

    def fetch_pylauncher(self):
        """Fetch the MSI for PyLauncher (required for Python2.x).
    
        It will be placed in the destination directory.
        """
        arch_tag = '.amd64' if (self.py_bitness == 64) else ''
        url = ("https://bitbucket.org/vinay.sajip/pylauncher/downloads/"
               "launchwin{0}.msi".format(arch_tag))
        target = pjoin(self.build_dir, 'launchwin{0}.msi'.format(arch_tag))
        if os.path.isfile(target):
            logger.info('PyLauncher MSI already in build directory.')
            return
        logger.info('Downloading PyLauncher MSI...')
        download(url, target)

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
    
    def write_script(self, entrypt, target):
        """Write a launcher script from a 'module:function' entry point
        
        python_version and bitness are used to write an appropriate shebang line
        for the PEP 397 Windows launcher.
        """
        module, func = entrypt.split(":")
        with open(target, 'w') as f:
            f.write(self.SCRIPT_TEMPLATE.format(qualifier=self.py_qualifier,
                                                module=module, func=func))

    def prepare_shortcuts(self):
        files = set()
        for scname, sc in self.shortcuts.items():
            if sc.get('entry_point'):
                sc['script'] = script = scname.replace(' ', '_') + '.launch.py'
                self.write_script(sc['entry_point'], pjoin(self.build_dir, script))
            else:
                shutil.copy2(sc['script'], self.build_dir)
        
            shutil.copy2(sc['icon'], self.build_dir)
            sc['icon'] = os.path.basename(sc['icon'])
            sc['script'] = os.path.basename(sc['script'])
            files.add(sc['script'])
            files.add(sc['icon'])
    
        self.install_files.extend(files)
    
    def prepare_packages(self):
        logger.info("Copying packages into build directory...")
        build_pkg_dir = pjoin(self.build_dir, 'pkgs')
        if os.path.isdir(build_pkg_dir):
            shutil.rmtree(build_pkg_dir)
        if os.path.isdir('pynsist_pkgs'):
            shutil.copytree('pynsist_pkgs', build_pkg_dir)
        else:
            os.mkdir(build_pkg_dir)
        copy_modules(self.packages, build_pkg_dir, py_version=self.py_version)

    def copy_extra_files(self):
        """Copy a list of files into the build directory, and add them to
        install_files or install_dirs as appropriate.
        """
        for file in self.extra_files:
            file = file.rstrip('/\\')
            basename = os.path.basename(file)
    
            if os.path.isdir(file):
                target_name = pjoin(self.build_dir, basename)
                if os.path.isdir(target_name):
                    shutil.rmtree(target_name)
                elif os.path.exists(target_name):
                    os.unlink(target_name)
                shutil.copytree(file, target_name)
                self.install_dirs.append(basename)
            else:
                shutil.copy2(file, self.build_dir)
                self.install_files.append(basename)
    
    def write_nsi(self):
        nsis_writer = NSISFileWriter(self.nsi_template, installerbuilder=self,
            definitions = {'PRODUCT_NAME': self.appname,
                           'PRODUCT_VERSION': self.version,
                           'PY_VERSION': self.py_version,
                           'PY_QUALIFIER': self.py_qualifier,
                           'PRODUCT_ICON': os.path.basename(self.icon),
                           'INSTALLER_NAME': self.installer_name,
                           'ARCH_TAG': '.amd64' if (self.py_bitness==64) else '',
                          },
            )

        logger.info('Writing NSI file to %s', self.nsi_file)
        nsis_writer.write(self.nsi_file)    

    def run_nsis(self):
        """Runs makensis using the specified .nsi file
        
        Returns the exit code.
        """
        try:
            if os.name == 'nt':
                makensis = pjoin(winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\NSIS'),
                                         'makensis.exe')
            else:
                makensis = 'makensis'
            return call([makensis, self.nsi_file])
        except OSError as e:
            # This should catch either the registry key or makensis being absent
            if e.errno == errno.ENOENT:
                print("makensis was not found. Install NSIS and try again.")
                print("http://nsis.sourceforge.net/Download")
                return 1

    def run(self):
        """Run all the steps to build an installer.
        """
        try:
            os.makedirs(self.build_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
        self.fetch_python()
        if PY2:
            self.fetch_pylauncher()
        
        self.prepare_shortcuts()
        
        # Packages
        self.prepare_packages()
        
        # Extra files
        self.copy_extra_files()

        self.write_nsi()
    
        exitcode = self.run_nsis()
        
        if not exitcode:
            logger.info('Installer written to %s', pjoin(self.build_dir, self.installer_name))

def main(argv=None):
    """Make an installer from the command line.
    
    This parses command line arguments and a config file, and calls
    :func:`all_steps` with the extracted information.
    """
    logger.setLevel(logging.INFO)
    logger.handlers = [logging.StreamHandler()]
    
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
        shortcuts = configreader.read_shortcuts_config(cfg)
    except configreader.InvalidConfig as e:
        logger.error('Error parsing configuration file:')
        logger.error(str(e))
        sys.exit(1)
    appcfg = cfg['Application']
    InstallerBuilder(
        appname = appcfg['name'],
        version = appcfg['version'],
        icon = appcfg.get('icon', DEFAULT_ICON),
        shortcuts = shortcuts,
        packages = cfg.get('Include', 'packages', fallback='').splitlines(),
        extra_files = cfg.get('Include', 'files', fallback='').splitlines(),
        py_version = cfg.get('Python', 'version', fallback=DEFAULT_PY_VERSION),
        py_bitness = cfg.getint('Python', 'bitness', fallback=DEFAULT_BITNESS),
        build_dir = cfg.get('Build', 'directory', fallback=DEFAULT_BUILD_DIR),
        installer_name = cfg.get('Build', 'installer_name', fallback=None),
        nsi_template = cfg.get('Build', 'nsi_template', fallback=DEFAULT_NSI_TEMPLATE),
    ).run()
