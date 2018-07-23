"""Build NSIS installers for Python applications.
"""
import errno
import io
import logging
import ntpath
import operator
import os
from pathlib import Path
import re
import shutil
from subprocess import call
import sys
import fnmatch
import zipfile

if os.name == 'nt':
    import winreg
else:
    winreg = None

from .configreader import get_installer_builder_args
from .commands import prepare_bin_directory
from .copymodules import copy_modules
from .nsiswriter import NSISFileWriter
from .pypi import fetch_pypi_wheels
from .util import download, text_types, get_cache_dir, normalize_path

__version__ = '2.1'

logger = logging.getLogger(__name__)

def pjoin(*args, **kwargs):
    newPath = ensurePathFormat(os.path.join(*args, **kwargs))
    return newPath

def ensurePathFormat(oldPath):
    newPath = re.sub("[/\\\\](?!\\\\)", "\\\\\\\\", oldPath)
    return newPath

_PKGDIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PY_VERSION = '3.6.3'
DEFAULT_BUILD_DIR = pjoin('build', 'nsis')
DEFAULT_ICON = pjoin(_PKGDIR, 'glossyorb.ico')
if os.name == 'nt' and sys.maxsize == (2**63)-1:
    DEFAULT_BITNESS = 64
else:
    DEFAULT_BITNESS = 32

def pjoin(*args, **kwargs):
    newPath = re.sub("[/\\\\](?!\\\\)", "\\\\\\\\", os.path.join(*args, **kwargs))
    return newPath

def find_makensis_win():
    """Locate makensis.exe on Windows by querying the registry"""
    try:
        nsis_install_dir = winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\NSIS')
    except OSError:
        nsis_install_dir = winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Wow6432Node\\NSIS')

    return pjoin(nsis_install_dir, 'makensis.exe')

class InputError(ValueError):
    def __init__(self, param, value, expected):
        self.param = param
        self.value = value
        self.expected = expected

    def __str__(self):
        return "{e.value!r} is not valid for {e.param}, expected {e.expected}".format(e=self)

class InstallerBuilder(object):
    """Controls building an installer. This includes three main steps:

    1. Arranging the necessary files in the build directory.
    2. Filling out the template NSI file to control NSIS.
    3. Running ``makensis`` to build the installer.

    :param str appname: Application name
    :param str version: Application version
    :param dict shortcuts: Dictionary keyed by shortcut name, containing
            dictionaries whose keys match the fields of :ref:`shortcut_config`
            in the config file
    :param str publisher: Publisher name
    :param str icon: Path to an icon for the application
    :param list packages: List of strings for importable packages to include
    :param dict commands: Dictionary keyed by command name, containing dicts
            defining the commands, as in the config file.
    :param list pypi_wheel_reqs: Package specifications to fetch from PyPI as wheels
    :param extra_wheel_sources: Directory paths to find wheels in.
    :type extra_wheel_sources: list of Path objects
    :param list extra_files: List of 2-tuples (file, destination) of files to include
    :param list exclude: Paths of files to exclude that would otherwise be included
    :param str py_version: Full version of Python to bundle
    :param int py_bitness: Bitness of bundled Python (32 or 64)
    :param str py_format: (deprecated) 'bundled'. Use Pynsist 1.x for
            'installer' option.
    :param bool inc_msvcrt: True to include the Microsoft C runtime with 'bundled'
            Python.
    :param str build_dir: Directory to run the build in
    :param str installer_name: Filename of the installer to produce
    :param str nsi_template: Path to a template NSI file to use
    :param list extra_installers: List of 4-tuples (file (str), message (str), type (int), condition (dict)) to other compiled installers to run
            The different types are as follows:
                0: The user does not have to do anything
                1: The user has to say yes or no
                2: The user has to click ok

            The condition should be None, a function, or a dictionary where the keys are different conditions and the values are functions that return strings.
            If multiple conditions are given, they must all pass to run the extra installer.
                If None: No conditions will be checked and the extra installer will run
                If Function: The extra installer will only run if the function returns True
                If Dictionary: The following are acceptable keys:
                    None: The function should return True or False

                    "inRegistry": The function should return a 4-tuple (root key (str), sub key (str), name (str), bitness (str))
                        The given registry entry must exist to run the extra installer
                        You can use http://www.nirsoft.net/utils/regscanner.html to search for they key you want.

                    "not_inRegistry": The function should return a 4-tuple (root key (str), sub key (str), name (str), bitness (str))
                        The given registry entry must not exist to run the extra installer

                    "contains": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must contain the given file to run the extra installer
                        * can be used for the given file to mean 'anything'; This will be a directory check instead of a file check
                        None will be interpreted as *

                    "not_contains": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must not contain the given file to run the extra installer
                        * can be used for the given file to mean 'anything'; This will be a directory check instead of a file check
                        None will be interpreted as *

                    "starts_with": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must contain the a file that starts with the given string to run the extra installer

                    "not_starts_with": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must not contain the a file that starts with the given string to run the extra installer

                    "ends_with": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must contain the a file that ends with the given string to run the extra installer

                    "not_ends_with": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must not contain the a file that ends with the given string to run the extra installer

                    "like": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must contain the a file that contains the given string anywhere to run the extra installer

                    "not_like": The function should return a 2-tuple (directory (str), file or sub directory (str))
                        The given directory must not contain the a file that contains the given string anywhere to run the extra installer
    """
    def __init__(self, appname, version, shortcuts, *, publisher=None,
                icon=DEFAULT_ICON, packages=None, extra_files=None,
                py_version=DEFAULT_PY_VERSION, py_bitness=DEFAULT_BITNESS,
                py_format='bundled', inc_msvcrt=True, build_dir=DEFAULT_BUILD_DIR,
                installer_name=None, nsi_template=None,
                exclude=None, pypi_wheel_reqs=None, extra_wheel_sources=None,
                commands=None, license_file=None, extra_installers=None):
        self.appname = appname
        self.version = version
        self.publisher = publisher
        self.shortcuts = shortcuts
        self.icon = icon
        self.packages = packages or []
        self.exclude = [normalize_path(p) for p in (exclude or [])]
        self.extra_files = extra_files or []
        self.pypi_wheel_reqs = pypi_wheel_reqs or []
        self.extra_wheel_sources = extra_wheel_sources or []
        self.commands = commands or {}
        self.license_file = license_file
        self.extra_installers = extra_installers or []
        self.has_checkRegistry = False
        self.has_checkDirContains = False
        self.has_checkDirStartsWith = False
        self.has_checkDirEndsWith = False
        self.has_checkDirLike = False

        # Python options
        self.py_version = py_version
        if not self._py_version_pattern.match(py_version):
            if not os.environ.get('PYNSIST_PY_PRERELEASE'):
                raise InputError('py_version', py_version,
                                 "a full Python version like '3.4.0'")
        if self.py_version_tuple < (3, 5):
            raise InputError('py_version', py_version,
                             "Python >= 3.5.0 (use Pynsist 1.x for older Python.")
        self.py_bitness = py_bitness
        if py_bitness not in {32, 64}:
            raise InputError('py_bitness', py_bitness, "32 or 64")
        self.py_major_version = self.py_qualifier = '.'.join(self.py_version.split('.')[:2])
        if self.py_bitness == 32:
            self.py_qualifier += '-32'

        if py_format == 'installer':
            raise InputError('py_format', py_format, "'bundled' (use Pynsist 1.x for 'installer')")
        elif py_format != 'bundled':
            raise InputError('py_format', py_format, "'bundled'")

        self.inc_msvcrt = inc_msvcrt

        # Build details
        self.build_dir = build_dir
        self.installer_name = installer_name or self.make_installer_name()
        self.nsi_template = nsi_template
        if self.nsi_template is None:
            if self.inc_msvcrt:
                self.nsi_template = 'pyapp_msvcrt.nsi'
            else:
                self.nsi_template = 'pyapp.nsi'

        self.nsi_file = pjoin(self.build_dir, 'installer.nsi')

        # To be filled later
        self.install_files = []
        self.install_dirs = []
        self.msvcrt_files = []

    _py_version_pattern = re.compile(r'\d\.\d+\.\d+$')

    @property
    def py_version_tuple(self):
        parts = self.py_version.split('.')
        return int(parts[0]), int(parts[1])

    def make_installer_name(self):
        """Generate the filename of the installer exe

        e.g. My_App_1.0.exe
        """
        s = self.appname + '_' + self.version + '.exe'
        return s.replace(' ', '_')

    def _python_download_url_filename(self):
        version = self.py_version
        bitness = self.py_bitness
        filename = 'python-{}-embed-{}.zip'.format(version,
                                   'amd64' if bitness==64 else 'win32')

        version_minus_prerelease = re.sub(r'(a|b|rc)\d+$', '', self.py_version)
        return 'https://www.python.org/ftp/python/{0}/{1}'.format(
                version_minus_prerelease, filename), filename

    def fetch_python_embeddable(self):
        """Fetch the embeddable Windows build for the specified Python version

        It will be unpacked into the build directory.

        In addition, any ``*._pth`` files found therein will have the pkgs path
        appended to them.
        """
        url, filename = self._python_download_url_filename()
        cache_file = get_cache_dir(ensure_existence=True) / filename
        if not cache_file.is_file():
            logger.info('Downloading embeddable Python build...')
            logger.info('Getting %s', url)
            download(url, cache_file)

        logger.info('Unpacking Python...')
        python_dir = pjoin(self.build_dir, 'Python')
        try:
            shutil.rmtree(python_dir)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        with zipfile.ZipFile(str(cache_file)) as z:
            z.extractall(python_dir)

        # Manipulate any *._pth files so the default paths AND pkgs directory
        # ends up in sys.path. Please see:
        # https://docs.python.org/3/using/windows.html#finding-modules
        # for more information.
        pth_files = [f for f in os.listdir(python_dir)
                     if os.path.isfile(pjoin(python_dir, f))
                     and f.endswith('._pth')]
        for pth in pth_files:
            with open(pjoin(python_dir, pth), 'a+b') as f:
                f.write(b'\r\n..\\pkgs\r\nimport site\r\n')

        self.install_dirs.append(('Python', '$INSTDIR'))

    def prepare_msvcrt(self):
        arch = 'x64' if self.py_bitness == 64 else 'x86'
        src = pjoin(_PKGDIR, 'msvcrt', arch)
        dst = pjoin(self.build_dir, 'msvcrt')
        self.msvcrt_files = sorted(os.listdir(src))

        try:
            shutil.rmtree(dst)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        shutil.copytree(src, dst)

    SCRIPT_TEMPLATE = """#!python{qualifier}
import sys, os
scriptdir, script = os.path.split(__file__)
installdir = scriptdir  # for compatibility with commands
pkgdir = os.path.join(scriptdir, 'pkgs')
sys.path.insert(0, pkgdir)
os.environ['PYTHONPATH'] = pkgdir + os.pathsep + os.environ.get('PYTHONPATH', '')

# APPDATA should always be set, but in case it isn't, try user home
# If none of APPDATA, HOME, USERPROFILE or HOMEPATH are set, this will fail.
appdata = os.environ.get('APPDATA', None) or os.path.expanduser('~')

if 'pythonw' in sys.executable:
    # Running with no console - send all stdstream output to a file.
    kw = {{'errors': 'replace'}} if (sys.version_info[0] >= 3) else {{}}
    sys.stdout = sys.stderr = open(os.path.join(appdata, script+'.log'), 'w', **kw)
else:
    # In a console. But if the console was started just for this program, it
    # will close as soon as we exit, so write the traceback to a file as well.
    def excepthook(etype, value, tb):
        "Write unhandled exceptions to a file and to stderr."
        import traceback
        traceback.print_exception(etype, value, tb)
        with open(os.path.join(appdata, script+'.log'), 'w') as f:
            traceback.print_exception(etype, value, tb, file=f)
    sys.excepthook = excepthook

{extra_preamble}

if __name__ == '__main__':
    from {module} import {func}
    {func}()
"""

    def write_script(self, entrypt, target, extra_preamble=''):
        """Write a launcher script from a 'module:function' entry point

        py_version and py_bitness are used to write an appropriate shebang line
        for the PEP 397 Windows launcher.
        """
        module, func = entrypt.split(":")
        with open(target, 'w') as f:
            f.write(self.SCRIPT_TEMPLATE.format(qualifier=self.py_qualifier,
                    module=module, func=func, extra_preamble=extra_preamble))

        pkg = module.split('.')[0]
        if pkg not in self.packages:
            self.packages.append(pkg)

    def prepare_shortcuts(self):
        """Prepare shortcut files in the build directory.

        If entry_point is specified, write the script. If script is specified,
        copy to the build directory. Prepare target and parameters for these
        shortcuts.

        Also copies shortcut icons.
        """
        files = set()
        for scname, sc in self.shortcuts.items():
            if not sc.get('target'):
                if sc.get('entry_point'):
                    sc['script'] = script = scname.replace(' ', '_') + '.launch.py' \
                                                + ('' if sc['console'] else 'w')

                    specified_preamble = sc.get('extra_preamble', None)
                    if isinstance(specified_preamble, text_types):
                        # Filename
                        extra_preamble = io.open(specified_preamble, encoding='utf-8')
                    elif specified_preamble is None:
                        extra_preamble = io.StringIO()  # Empty
                    else:
                        # Passed a StringIO or similar object
                        extra_preamble = specified_preamble

                    self.write_script(sc['entry_point'], pjoin(self.build_dir, script),
                                      extra_preamble.read().rstrip())
                else:
                    shutil.copy2(sc['script'], self.build_dir)

                target = '$INSTDIR\Python\python{}.exe'
                sc['target'] = target.format('' if sc['console'] else 'w')
                sc['parameters'] = '"%s"' % ntpath.join('$INSTDIR', sc['script'])
                files.add(os.path.basename(sc['script']))

            shutil.copy2(sc['icon'], self.build_dir)
            sc['icon'] = os.path.basename(sc['icon'])
            files.add(sc['icon'])
        self.install_files.extend([(f, '$INSTDIR') for f in files])

    def copy_license(self):
        """
        If a license file has been specified, ensure it's copied into the
        install directory and added to the install_files list.
        """
        if self.license_file:
            shutil.copy2(self.license_file, self.build_dir)
            license_file_name = os.path.basename(self.license_file)
            self.install_files.append((license_file_name, '$INSTDIR'))


    def prepare_packages(self):
        """Move requested packages into the build directory.

        If a pynsist_pkgs directory exists, it is copied into the build
        directory as pkgs/ . Any packages not already there are found on
        sys.path and copied in.
        """
        logger.info("Copying packages into build directory...")
        build_pkg_dir = pjoin(self.build_dir, 'pkgs')
        if os.path.isdir(build_pkg_dir):
            shutil.rmtree(build_pkg_dir)

        # 1. Manually prepared packages
        if os.path.isdir('pynsist_pkgs'):
            shutil.copytree('pynsist_pkgs', build_pkg_dir)
        else:
            os.mkdir(build_pkg_dir)

        # 2. Wheels from PyPI
        fetch_pypi_wheels(self.pypi_wheel_reqs, build_pkg_dir,
                          py_version=self.py_version, bitness=self.py_bitness,
                          extra_sources=self.extra_wheel_sources,
                          exclude=self.exclude)

        # 3. Copy importable modules
        copy_modules(self.packages, build_pkg_dir,
                     py_version=self.py_version, exclude=self.exclude)

    def prepare_commands(self):
        command_dir = Path(self.build_dir) / 'bin'
        if command_dir.is_dir():
            shutil.rmtree(str(command_dir))
        command_dir.mkdir()
        prepare_bin_directory(command_dir, self.commands, bitness=self.py_bitness)
        self.install_dirs.append((command_dir.name, '$INSTDIR'))
        self.extra_files.append((pjoin(_PKGDIR, '_system_path.py'), '$INSTDIR'))
        self.extra_files.append((pjoin(_PKGDIR, '_rewrite_shebangs.py'), '$INSTDIR'))

    def copytree_ignore_callback(self, directory, files):
        """This is being called back by our shutil.copytree call to implement the
        'exclude' feature.
        """
        ignored = set()

        # Filter by file names relative to the build directory
        directory = os.path.normpath(directory)
        files = [os.path.join(directory, fname) for fname in files]

        # Execute all patterns
        for pattern in self.exclude:
            ignored.update([
                os.path.basename(fname)
                for fname in fnmatch.filter(files, pattern)
            ])
        return ignored

    def copy_extra_files(self):
        """Copy a list of files into the build directory, and add them to
        install_files or install_dirs as appropriate.
        """
        for file, destination in self.extra_files:
            file = file.rstrip('/\\')
            basename = os.path.basename(file)

            if not destination:
                destination = '$INSTDIR'

            if os.path.isdir(file):
                target_name = pjoin(self.build_dir, basename)
                if os.path.isdir(target_name):
                    shutil.rmtree(target_name)
                elif os.path.exists(target_name):
                    os.unlink(target_name)
                if self.exclude:
                    shutil.copytree(file, target_name,
                                    ignore=self.copytree_ignore_callback)
                else:
                    # Don't use our exclude callback if we don't need to,
                    # as it slows things down.
                    shutil.copytree(file, target_name)
                self.install_dirs.append((basename, destination))
            else:
                shutil.copy2(file, self.build_dir)
                self.install_files.append((basename, destination))

    def prepare_extra_installers(self):
        """Copies the extra installers into the build directory
        """

        for file, _, _, _ in self.extra_installers:
            file = file.rstrip('/\\')
            basename = os.path.basename(file)

            shutil.copy2(file, self.build_dir)
            self.install_files.append((basename, '$INSTDIR\Prerequisites'))

            #Run to set 'has_' variables
            self.apply_extra_installers()

    def apply_extra_installers(self):
        """Returns NSI code for the extra installers.
        See: http://nsis.sourceforge.net/Embedding_other_installers
        """

        def escapeNewLine(oldText):
            newText = re.sub("\n", "\\\\n", oldText)
            return newText

        def checkRegistry(rootKey, subKey, name, bitness, *args, indent = 2, **kwargs):
            self.has_checkRegistry = True
            code = f'{" "*indent}${{checkRegistry}} "{escapeNewLine(rootKey)}" "{escapeNewLine(subKey)}" "{escapeNewLine(name)}" "{bitness}" \n'
            code += evaluateAnswer(*args, indent = indent, **kwargs)
            return code

        def checkDirContains(dirPath, filePath, *args, indent = 2, **kwargs):
            self.has_checkDirContains = True
            if (not filePath):
                filePath = "*"
            code = f'{" "*indent}${{checkDirContains}} "{escapeNewLine(ensurePathFormat(dirPath))}" "{escapeNewLine(ensurePathFormat(filePath))}"\n'
            code += evaluateAnswer(*args, indent = indent, **kwargs)
            return code

        def checkDirStartsWith(dirPath, filePath, *args, indent = 2, **kwargs):
            self.has_checkDirStartsWith = True
            code = f'{" "*indent}${{checkDirStartsWith}} "{escapeNewLine(ensurePathFormat(dirPath))}" "{escapeNewLine(ensurePathFormat(filePath))}"\n'
            code += evaluateAnswer(*args, indent = indent, **kwargs)
            return code

        def checkDirEndsWith(dirPath, filePath, *args, indent = 2, **kwargs):
            self.has_checkDirEndsWith = True
            code = f'{" "*indent}${{checkDirEndsWith}} "{escapeNewLine(ensurePathFormat(dirPath))}" "{escapeNewLine(ensurePathFormat(filePath))}"\n'
            code += evaluateAnswer(*args, indent = indent, **kwargs)
            return code

        def checkDirLike(dirPath, filePath, *args, indent = 2, **kwargs):
            self.has_checkDirLike = True
            code = f'{" "*indent}${{checkDirLike}} "{escapeNewLine(ensurePathFormat(dirPath))}" "{escapeNewLine(ensurePathFormat(filePath))}"\n'
            code += evaluateAnswer(*args, indent = indent, **kwargs)
            return code

        def evaluateAnswer(ifTrue = None, ifFalse = None, showDebugMessages = False, indent = 2):
            code = f'{" "*indent}${{If}} $str_returnVar == "true"\n'
            if (showDebugMessages):
                # code += DetailPrint 
                code += f'{" "*indent}  MessageBox MB_OK "True"\n'
            if (ifTrue):
                code += f'{" "*indent}  Goto {ifTrue}\n'
            
            code += f'{" "*indent}${{Else}}\n'
            if (showDebugMessages):
                code += f'{" "*indent}  MessageBox MB_OK "False"\n'
            if (ifFalse):
                code += f'{" "*indent}  Goto {ifFalse}\n'

            code += f'{" "*indent}${{EndIf}}\n'
            return code

        code = 'SetOutPath "$INSTDIR\\\\Prerequisites"\n'
        for i, (file, message, installType, condition) in enumerate(self.extra_installers):
            file = file.rstrip('/\\')
            basename = os.path.basename(file)
            message = re.sub("(?<!\$)\n", "$\n", message) #Account for new lines

            code += f"  Goto prereq_{i}.0_start\n"
            code += f"  prereq_{i}.0_start:\n"
            try:
                if (condition != None):
                    if (not isinstance(condition, dict)):
                        condition = {None: condition}

                    nextInstaller = True
                    for j, (conditionType, function) in enumerate(condition.items()):
                        if (callable(function)):
                            answer = function()
                        else:
                            answer = function

                        if (not conditionType):
                            if (not answer):
                                code += f"    Goto prereq_{i}.0_end\n"
                            break

                        elif (conditionType == "inRegistry"):
                            code += checkRegistry(answer[0], answer[1], answer[2], answer[3], ifFalse = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "not_inRegistry"):
                            code += checkRegistry(answer[0], answer[1], answer[2], answer[3], ifTrue = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "contains"):
                            code += checkDirContains(answer[0], answer[1], ifFalse = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "not_contains"):
                            code += checkDirContains(answer[0], answer[1], ifTrue = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "starts_with"):
                            code += checkDirStartsWith(answer[0], answer[1], ifFalse = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "not_starts_with"):
                            code += checkDirStartsWith(answer[0], answer[1], ifTrue = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "ends_with"):
                            code += checkDirEndsWith(answer[0], answer[1], ifFalse = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "not_ends_with"):
                            code += checkDirEndsWith(answer[0], answer[1], ifTrue = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "like"):
                            code += checkDirLike(answer[0], answer[1], ifFalse = f"prereq_{i}.0_end", indent = 4)

                        elif (conditionType == "not_like"):
                            code += checkDirLike(answer[0], answer[1], ifTrue = f"prereq_{i}.0_end", indent = 4)

                        else:
                            raise InputError('condition key', conditionType, "unknown condition key")
                    else:
                        nextInstaller = False
                    if (nextInstaller):
                        continue

                if (installType == 1):
                    #The user has to say yes or no
                    code += f"""    MessageBox MB_YESNO "{escapeNewLine(message) or f'Install {escapeNewLine(basename)}?'}" /SD IDYES IDNO prereq_{i}.0_end\n"""

                elif (installType == 2):
                    #The user has to say ok
                    code += f"""    MessageBox MB_Ok "{escapeNewLine(message) or f'Press Ok to Install {escapeNewLine(basename)}'}"\n"""

                #Run the installer
                code += f"    Goto prereq_{i}.1_start\n"
                code += f"    prereq_{i}.1_start:\n"
                if (basename.endswith(".exe")):
                    code += f"""      ExecWait "$INSTDIR\Prerequisites\{escapeNewLine(basename)}"\n"""
                elif(basename.endswith(".msi")):
                    code += f"""      ExecWait '"msiexec" /i "$INSTDIR\Prerequisites\{escapeNewLine(basename)}"'\n"""
                else:
                    raise InputError('extra_installers file', file, "unknown file type")
                code += f"      Goto prereq_{i}.0_end\n"

            finally:
                code += f"  prereq_{i}.0_end:\n"

        return code.rstrip("\n")

    def write_nsi(self):
        """Write the NSI file to define the NSIS installer.

        Most of the details of this are in the template and the
        :class:`nsist.nsiswriter.NSISFileWriter` class.
        """
        nsis_writer = NSISFileWriter(self.nsi_template, installerbuilder=self)

        logger.info('Writing NSI file to %s', self.nsi_file)
        # Sort by destination directory, so we can group them effectively
        self.install_files.sort(key=operator.itemgetter(1))
        nsis_writer.write(self.nsi_file)

    def run_nsis(self):
        """Runs makensis using the specified .nsi file

        Returns the exit code.
        """
        try:
            if os.name == 'nt':
                makensis = find_makensis_win()
            else:
                makensis = 'makensis'
            logger.info('\n~~~ Running makensis ~~~')
            return call([makensis, self.nsi_file])
        except OSError as e:
            # This should catch either the registry key or makensis being absent
            if e.errno == errno.ENOENT:
                print("makensis was not found. Install NSIS and try again.")
                print("http://nsis.sourceforge.net/Download")
                return 1

    def run(self, makensis=True):
        """Run all the steps to build an installer.
        """
        try:
            os.makedirs(self.build_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e

        self.fetch_python_embeddable()
        if self.inc_msvcrt:
            self.prepare_msvcrt()

        self.prepare_shortcuts()

        self.copy_license()

        if self.commands:
            self.prepare_commands()

        # Packages
        self.prepare_packages()

        # Extra files
        self.copy_extra_files()

        # Extra installers
        if self.extra_installers:
            self.prepare_extra_installers()

        self.write_nsi()

        if makensis:
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
    argp.add_argument('--no-makensis', action='store_true',
        help='Prepare files and folders, stop before calling makensis. For debugging.'
    )
    options = argp.parse_args(argv)

    dirname, config_file = os.path.split(options.config_file)
    if dirname:
        os.chdir(dirname)

    from . import configreader
    try:
        cfg = configreader.read_and_validate(config_file)
    except configreader.InvalidConfig as e:
        logger.error('Error parsing configuration file:')
        logger.error(str(e))
        sys.exit(1)

    args = get_installer_builder_args(cfg)

    try:
        InstallerBuilder(**args).run(makensis=(not options.no_makensis))
    except InputError as e:
        logger.error("Error in config values:")
        logger.error(str(e))
        sys.exit(1)
