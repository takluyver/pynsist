import itertools
from operator import itemgetter
import os
import ntpath
import re
import sys

import jinja2

_PKGDIR = os.path.abspath(os.path.dirname(__file__))

PY2 = sys.version_info[0] == 2


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
        grouped_files = [(dest, [x[0] for x in group]) for (dest, group) in
            itertools.groupby(self.installerbuilder.install_files, itemgetter(1))
                ]

        self.namespace = {
            'ib': installerbuilder,
            'grouped_files': grouped_files,
            'icon': os.path.basename(installerbuilder.icon),
            'arch_tag': '.amd64' if (installerbuilder.py_bitness==64) else '',
            'pjoin': ntpath.join,
            'single_shortcut': len(installerbuilder.shortcuts) == 1,
            'pynsist_pkg_dir': _PKGDIR,
            'has_commands': len(installerbuilder.commands) > 0,
        }

        if installerbuilder.py_format == 'bundled':
            self.namespace['python'] = '"$INSTDIR\\Python\\python"'
        else:
            self.namespace['python'] = 'py -{}'.format(installerbuilder.py_qualifier)

    def write(self, target):
        """Fill out the template and write the result to 'target'.
        
        :param str target: Path to the file to be written
        """
        with open(target, 'w') as fout:
            fout.write(self.template.render(self.namespace))

