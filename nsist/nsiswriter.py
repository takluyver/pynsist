import itertools
import operator
import ntpath
import re
import sys

PY2 = sys.version_info[0] == 2


class NSISFileWriter(object):
    """Write an .nsi script file by filling in a template.
    """
    def __init__(self, template_file, installerbuilder, definitions=None):
        """Instantiate an NSISFileWriter
        
        :param str template_file: Path to the .nsi template
        :param dict definitions: Mapping of name to value (values will be quoted)
        """
        self.template_file = template_file
        self.installerbuilder = installerbuilder
        self.definitions = definitions or {}
        self.template_fields = {
                ';INSTALL_FILES': self.files_install,
                ';INSTALL_DIRECTORIES': self.dirs_install,
                ';INSTALL_SHORTCUTS': self.shortcuts_install,
                ';UNINSTALL_FILES': self.files_uninstall,
                ';UNINSTALL_DIRECTORIES': self.dirs_uninstall,
                ';UNINSTALL_SHORTCUTS': self.shortcuts_uninstall,
        }
        if PY2:
            self.template_fields.update({
                ';PYLAUNCHER_INSTALL': self.pylauncher_install,
                ';PYLAUNCHER_HELP': self.pylauncher_help})

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

    def write_definitions(self, f):
        """Write definition lines at the start of the file.
        
        :param f: A text-mode writable file handle
        """
        for name, value in self.definitions.items():
            f.write('!define {} "{}"\n'.format(name, value))

    # Template fillers
    # ----------------

    # These return an iterable of lines to fill after a given template field

    def files_install(self):
        for destination, group in itertools.groupby(
                    self.installerbuilder.install_files, operator.itemgetter(1)):
            yield 'SetOutPath "{}"'.format(destination)
            for file, _ in group:
                yield 'File "{}"'.format(file)
        yield 'SetOutPath "$INSTDIR"'

    def dirs_install(self):
        for dir, destination in self.installerbuilder.install_dirs:
            yield 'SetOutPath "{}"'.format(ntpath.join(destination, dir))
            yield 'File /r "{}\*.*"'.format(dir)
        yield 'SetOutPath "$INSTDIR"'
    
    def shortcuts_install(self):
        shortcuts = self.installerbuilder.shortcuts
        # The output path becomes the working directory for shortcuts.
        yield 'SetOutPath "%HOMEDRIVE%\\%HOMEPATH%"'
        if len(shortcuts) == 1:
            scname, sc = next(iter(shortcuts.items()))
            yield 'CreateShortCut "$SMPROGRAMS\{}.lnk" "{}" \'"$INSTDIR\{}"\' \\'.format(\
                    scname, ('py' if sc['console'] else 'pyw'), sc['script'])
            yield '    "$INSTDIR\{}"'.format(sc['icon'])
            yield 'SetOutPath "$INSTDIR"'
            return
        
        # Multiple shortcuts - make a folder
        yield 'CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"'
        for scname, sc in shortcuts.items():
            yield 'CreateShortCut "$SMPROGRAMS\${{PRODUCT_NAME}}\{}.lnk" "{}" \\'.format(\
                    scname, sc['target'])
            yield '    \'{}\' "$INSTDIR\{}"'.format(sc['parameters'], sc['icon'])
        yield 'SetOutPath "$INSTDIR"'

    def files_uninstall(self):
        for file, destination in self.installerbuilder.install_files:
            yield 'Delete "{}"'.format(ntpath.join(destination, file))

    def dirs_uninstall(self):
        for dir, destination in self.installerbuilder.install_dirs:
            yield 'RMDir /r "{}"'.format(ntpath.join(destination, dir))
    
    def shortcuts_uninstall(self):
        shortcuts = self.installerbuilder.shortcuts
        if len(shortcuts) == 1:
            scname = next(iter(shortcuts))
            yield 'Delete "$SMPROGRAMS\{}.lnk"'.format(scname)
        else:
            yield 'RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"'

    def pylauncher_install(self):
        return ["Section \"PyLauncher\" sec_pylauncher",
            "    File \"launchwin${ARCH_TAG}.msi\"",
            "    ExecWait 'msiexec /i \"$INSTDIR\launchwin${ARCH_TAG}.msi\" /qb ALLUSERS=1'",
            "    Delete $INSTDIR\launchwin${ARCH_TAG}.msi",
            "SectionEnd",
           ]

    def pylauncher_help(self):
        return ["StrCmp $0 ${sec_pylauncher} 0 +2",
                "SendMessage $R0 ${WM_SETTEXT} 0 \"STR:The Python launcher. \\",
                "    This is required for ${PRODUCT_NAME} to run.\"",
               ]