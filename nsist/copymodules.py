import importlib, importlib.abc
import os
import shutil
import sys
import zipfile, zipimport

class ModuleCopier:
    def __init__(self, path=None):
        self.path = path if (path is not None) else ([''] + sys.path)
    
    def copy(self, modname, target):
        loader = importlib.find_loader(modname, self.path)
        if loader is None:
            raise ImportError('Could not find %s' % modname)
        pkg = loader.is_package(modname)
        file = loader.get_filename(modname)
        if isinstance(loader, importlib.abc.FileLoader):
            if pkg:
                pkgdir, basename = os.path.split(file)
                assert basename.startswith('__init__')
                dest = os.path.join(target, modname)
                shutil.copytree(pkgdir, dest, ignore=shutil.ignore_patterns('*.pyc'))
            else:                
                shutil.copy2(file, target)
        
        elif isinstance(loader, zipimport.zipimporter):
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