import re

class NSISFileWriter(object):
    def __init__(self, template_file, definitions=None):
        self.template_file = template_file
        self.definitions = definitions or {}
        self.extra_files = []
        self.write_after_line = {
                ';EXTRA_FILES_INSTALL': self.write_extra_files_install,
                ';EXTRA_FILES_UNINSTALL': self.write_extra_files_uninstall,
        }
    
    def write_definitions(self, f):
        for name, value in self.definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))
    
    def write_extra_files_install(self, f, indent):
        for file, is_dir in self.extra_files:
            if is_dir:
                f.write(indent+'SetOutPath "$INSTDIR\{}"\n'.format(file))
                f.write(indent+'File /r "{}\*.*"\n'.format(file))
                f.write(indent+'SetOutPath "$INSTDIR"\n')
            else:
                f.write(indent+'File "{}"\n'.format(file))

    def write_extra_files_uninstall(self, f, indent):
        for file, is_dir in self.extra_files:
            if is_dir:
                f.write(indent+'RMDir /r "$INSTDIR\{}"\n'.format(file))
            else:
                f.write(indent+'Delete "$INSTDIR\{}"\n'.format(file))
    
    def write(self, target):
        with open(target, 'w') as fout, open(self.template_file) as fin:
            self.write_definitions(fout)
            
            for line in fin:
                fout.write(line)
                l = line.strip()
                if l in self.write_after_line:
                    indent = re.match('\s*', line).group(0)
                    self.write_after_line[l](fout, indent)