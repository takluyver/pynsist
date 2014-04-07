import importlib, importlib.abc, importlib.machinery
import os
import shutil
import sys
import zipfile, zipimport

class ModuleCopier:
    """Finds and copies importable Python modules and packages.
    
    This uses importlib to locate modules.
    """
    def __init__(self, path=None):
        self.path = path if (path is not None) else ([''] + sys.path)
    
    def copy(self, modname, target):
        """Copy the importable module 'modname' to the directory 'target'.
        
        modname should be a top-level import, i.e. without any dots. Packages
        are always copied whole.
        
        This can currently copy regular filesystem files and directories, and
        extract modules and packages from appropriately structured zip files.
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
                shutil.copytree(pkgdir, dest, ignore=shutil.ignore_patterns('*.pyc'))
            else:                
                shutil.copy2(file, target)
        
        elif isinstance(loader, zipimport.zipimporter):
            file = loader.get_filename(modname)
            prefix = loader.archive + '/' + loader.prefix
            assert file.startswith(prefix)
            path_in_zip = file[len(prefix):]
            zf = zipfile.ZipFile(loader.archive)
            if pkg:
                pkgdir, basename = path_in_zip.rsplit('/', 1)
                assert basename.startswith('__init__')
                pkgfiles = [f for f in zf.namelist() if f.startswith(pkgdir)]
                zf.extractall(target, pkgfiles)
            else:
                zf.extract(path_in_zip, target)

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
