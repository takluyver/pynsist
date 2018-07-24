import itertools
from operator import itemgetter
import os
import ntpath
import re
import sys

import jinja2

_PKGDIR = os.path.abspath(os.path.dirname(__file__))

PY2 = sys.version_info[0] == 2

def pjoin(*args, **kwargs):
    newPath = ensurePathFormat(ntpath.join(*args, **kwargs))
    return newPath

def ensurePathFormat(oldPath):
    newPath = re.sub("[/\\\\](?!\\\\)", "\\\\\\\\", oldPath)
    return newPath

class NSISFileWriter(object):
    """Write an .nsi script file by filling in a template.
    """
    def __init__(self, template_file, installerbuilder, definitions=None):
        """Instantiate an NSISFileWriter
        
        :param str template_file: Path to the .nsi template
        :param dict definitions: Mapping of name to value (values will be quoted)
        """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader([
            _PKGDIR,
            os.getcwd()
        ]),
        # Change template markers from {}, which NSIS uses, to [], which it
        # doesn't much, so it's easier to distinguishing our templating from
        # NSIS preprocessor variables.
        block_start_string="[%",
        block_end_string="%]",
        variable_start_string="[[",
        variable_end_string="]]",
        comment_start_string="[#",
        comment_end_string="#]",

        # Trim whitespace around block tags, so formatting works as I expect
        trim_blocks=True,
        lstrip_blocks=True,
        )
        self.template = env.get_template(template_file)
        self.installerbuilder = installerbuilder

        # Group files by their destination directory
        grouped_files = [(dest, [(x[0], installerbuilder.extra_files_buildName.get(x, x[0])) for x in group]) for (dest, group) in
            itertools.groupby(self.installerbuilder.install_files, itemgetter(1))
                ]

        license_file = None
        if installerbuilder.license_file:
            license_file = os.path.basename(installerbuilder.license_file)
        self.namespace = {
            'ib': installerbuilder,
            'grouped_files': grouped_files,
            'icon': os.path.basename(installerbuilder.icon),
            'arch_tag': '.amd64' if (installerbuilder.py_bitness==64) else '',
            'pjoin': pjoin,
            'ensurePathFormat': ensurePathFormat,
            'single_shortcut': len(installerbuilder.shortcuts) == 1,
            'pynsist_pkg_dir': _PKGDIR,
            'has_commands': len(installerbuilder.commands) > 0,
            'has_prereq': len(installerbuilder.extra_installers) > 0,
            'gen_prereq': installerbuilder.apply_extra_installers,
            'has_checkRegistry': installerbuilder.has_checkRegistry,
            'has_checkDirContains': installerbuilder.has_checkDirContains,
            'has_checkDirStartsWith': installerbuilder.has_checkDirStartsWith,
            'has_checkDirEndsWith': installerbuilder.has_checkDirEndsWith,
            'has_checkDirLike': installerbuilder.has_checkDirLike,
            'python': '"$INSTDIR\\Python\\python"',
            'license_file': license_file,
        }

    def write(self, target):
        """Fill out the template and write the result to 'target'.
        
        :param str target: Path to the file to be written
        """
        with open(target, 'w') as fout:
            fout.write(self.template.render(self.namespace))

