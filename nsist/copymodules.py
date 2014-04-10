import os
import shutil
import sys
import zipfile, zipimport

PY2 = sys.version_info[0] == 2


def copy_zipmodule(loader, modname, target):
    file = loader.get_filename(modname)
    prefix = loader.archive + '/' + loader.prefix
    assert file.startswith(prefix)
    path_in_zip = file[len(prefix):]
    zf = zipfile.ZipFile(loader.archive)
    if loader.is_package(modname):
        pkgdir, basename = path_in_zip.rsplit('/', 1)
        assert basename.startswith('__init__')
        pkgfiles = [f for f in zf.namelist() if f.startswith(pkgdir)]
        zf.extractall(target, pkgfiles)
    else:
        zf.extract(path_in_zip, target)

if not PY2:
    import importlib
    import importlib.abc
    import importlib.machinery

    class ModuleCopier:
        """Finds and copies importable Python modules and packages.

        This is the Python >3.3 version and uses the `importlib` package to
        locate modules.
        """
        def __init__(self, path=None):
            self.path = path if (path is not None) else ([''] + sys.path)

        def copy(self, modname, target):
            """Copy the importable module 'modname' to the directory 'target'.

            modname should be a top-level import, i.e. without any dots.
            Packages are always copied whole.

            This can currently copy regular filesystem files and directories,
            and extract modules and packages from appropriately structured zip
            files.
            """
            loader = importlib.find_loader(modname, self.path)
            if loader is None:
                raise ImportError('Could not find %s' % modname)
            pkg = loader.is_package(modname)

            if isinstance(loader, importlib.machinery.ExtensionFileLoader):
                shutil.copy2(loader.path, target)

            elif isinstance(loader, importlib.abc.FileLoader):
                file = loader.get_filename(modname)
                if pkg:
                    pkgdir, basename = os.path.split(file)
                    assert basename.startswith('__init__')
                    dest = os.path.join(target, modname)
                    shutil.copytree(pkgdir, dest,
                                    ignore=shutil.ignore_patterns('*.pyc'))
                else:
                    shutil.copy2(file, target)

            elif isinstance(loader, zipimport.zipimporter):
                copy_zipmodule(loader, modname, target)
else:
    import imp

    class ModuleCopier:
        """Finds and copies importable Python modules and packages.

        This is the Python 2.7 version and uses the `imp` package to locate
        modules.
        """
        def __init__(self, path=None):
            self.path = path if (path is not None) else ([''] + sys.path)
            self.zip_paths = [p for p in self.path if zipfile.is_zipfile(p)]

        def copy(self, modname, target):
            """Copy the importable module 'modname' to the directory 'target'.

            modname should be a top-level import, i.e. without any dots.
            Packages are always copied whole.

            This can currently copy regular filesystem files and directories,
            and extract modules and packages from appropriately structured zip
            files.
            """
            info = imp.find_module(modname, self.path)
            path = info[1]
            modtype = info[2][2]

            if modtype in (imp.PY_SOURCE, imp.C_EXTENSION):
                shutil.copy2(path, target)

            elif modtype == imp.PKG_DIRECTORY:
                dest = os.path.join(target, modname)
                shutil.copytree(path, dest,
                                ignore=shutil.ignore_patterns('*.pyc'))
            else:
                # Search all ZIP files in self.path for the module name
                # NOTE: `imp.find_module(...)` will *not* find modules in ZIP
                #       files, so we have to check each file for ourselves
                for zpath in self.zip_path:
                    loader = zipimport.zipimporter(zpath)
                    if loader.find_module(modname) is None:
                        continue
                    copy_zipmodule(loader, modname, target)


def copy_modules(modnames, target, path=None):
    """Copy the specified importable modules to the target directory.
    
    By default, it finds modules in sys.path - this can be overridden by passing
    the path parameter.
    """
    mc = ModuleCopier(path)
    files_in_target_noext = [os.path.splitext(f)[0] for f in os.listdir(target)]
    
    for modname in modnames:
        if modname in files_in_target_noext:
            # Already there, no need to copy it.
            continue
        mc.copy(modname, target)
    
    if not modnames:
        # NSIS abhors an empty folder, so give it a file to find.
        with open(os.path.join(target, 'placeholder'), 'w') as f:
            f.write('This file only exists so NSIS finds something in this directory.')
