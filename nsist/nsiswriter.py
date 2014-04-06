import re

class NSISFileWriter(object):
    """Write an .nsi script file by filling in a template.
    """
    def __init__(self, template_file, definitions=None):
        """Instantiate an NSISFileWriter
        
        :param str template_file: Path to the .nsi template
        :param dict definitions: Mapping of name to value (values will be quoted)
        """
        self.template_file = template_file
        self.definitions = definitions or {}
        self.extra_files = []
        self.write_after_line = {
                ';EXTRA_FILES_INSTALL': self.write_extra_files_install,
                ';EXTRA_FILES_UNINSTALL': self.write_extra_files_uninstall,
        }
    
    def write_definitions(self, f):
        """Write definition lines at the start of the file.
        
        :param f: A text-mode writable file handle
        """
        for name, value in self.definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))
    
    def write_extra_files_install(self, f, indent):
        """Write the commands to install the list of extra files and directories.
        
        :param f: A text-mode writable file handle
        :param str indent: Leading space at this point in the file
        """
        for file, is_dir in self.extra_files:
            if is_dir:
                f.write(indent+'SetOutPath "$INSTDIR\{}"\n'.format(file))
                f.write(indent+'File /r "{}\*.*"\n'.format(file))
                f.write(indent+'SetOutPath "$INSTDIR"\n')
            else:
                f.write(indent+'File "{}"\n'.format(file))

    def write_extra_files_uninstall(self, f, indent):
        """Write the commands to uninstall the list of extra files and directories.
        
        :param f: A text-mode writable file handle
        :param str indent: Leading space at this point in the file
        """
        for file, is_dir in self.extra_files:
            if is_dir:
                f.write(indent+'RMDir /r "$INSTDIR\{}"\n'.format(file))
            else:
                f.write(indent+'Delete "$INSTDIR\{}"\n'.format(file))
    
    def write(self, target):
        """Fill out the template and write the result to 'target'.
        
        :param str target: Path to the file to be written
        """
        with open(target, 'w') as fout, open(self.template_file) as fin:
            self.write_definitions(fout)
            
            for line in fin:
                fout.write(line)
                l = line.strip()
                if l in self.write_after_line:
                    indent = re.match('\s*', line).group(0)
                    self.write_after_line[l](fout, indent)