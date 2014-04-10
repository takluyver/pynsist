import re
import sys

PY2 = sys.version_info[0] == 2


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
        self.template_fields = {
                ';EXTRA_FILES_INSTALL': self.make_extra_files_install,
                ';EXTRA_FILES_UNINSTALL': self.make_extra_files_uninstall,
        }
        if PY2:
            self.template_fields.update({
                ';PYLAUNCHER_INSTALL': self.make_pylauncher_install,
                ';PYLAUNCHER_HELP': self.make_pylauncher_help})

    def write_definitions(self, f):
        """Write definition lines at the start of the file.
        
        :param f: A text-mode writable file handle
        """
        for name, value in self.definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))
    
    def make_extra_files_install(self):
        """Write the commands to install the list of extra files and directories.
        
        :param f: A text-mode writable file handle
        :param str indent: Leading space at this point in the file
        """
        for file, is_dir in self.extra_files:
            if is_dir:
                yield 'SetOutPath "$INSTDIR\{}"\n'.format(file)
                yield 'File /r "{}\*.*"\n'.format(file)
                yield 'SetOutPath "$INSTDIR"\n'
            else:
                yield 'File "{}"\n'.format(file)

    def make_extra_files_uninstall(self):
        """Write the commands to uninstall the list of extra files and directories.
        
        :param f: A text-mode writable file handle
        :param str indent: Leading space at this point in the file
        """
        for file, is_dir in self.extra_files:
            if is_dir:
                yield 'RMDir /r "$INSTDIR\{}"\n'.format(file)
            else:
                yield 'Delete "$INSTDIR\{}"\n'.format(file)

    def make_pylauncher_install(self):
        return ["Section \"PyLauncher\" sec_pylauncher",
            "    File \"launchwin${ARCH_TAG}.msi\"",
            "    ExecWait 'msiexec /i \"$INSTDIR\launchwin${ARCH_TAG}.msi\" /qb ALLUSERS=1'",
            "    Delete $INSTDIR\launchwin${ARCH_TAG}.msi",
            "SectionEnd",
           ]

    def make_pylauncher_help(self):
        return ["StrCmp $0 ${sec_pylauncher} 0 +2",
                "SendMessage $R0 ${WM_SETTEXT} 0 \"STR:The Python launcher. \\",
                "    This is required for ${PRODUCT_NAME} to run.\"",
               ]

    def write(self, target):
        """Fill out the template and write the result to 'target'.
        
        :param str target: Path to the file to be written
        """
        with open(target, 'w') as fout, open(self.template_file) as fin:
            self.write_definitions(fout)
            
            for line in fin:
                fout.write(line)
                l = line.strip()
                if l in self.template_fields:
                    indent = re.match('\s*', line).group(0)
                    for fillline in self.template_fields[l]():
                        fout.write(indent+fillline+'\n')