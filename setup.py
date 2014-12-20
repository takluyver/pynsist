import os
import re
import sys
from distutils.core import setup
from distutils.command.build_scripts import build_scripts
from distutils import log

PY2 = sys.version_info[0] == 2

requirements = ['requests',
                'jinja2',
               ]
if PY2:
    requirements.append('configparser >= 3.3.0r2')

with open('README.rst', 'r') as f:
    readme=f.read()

# We used to just import the version number here. But you can't import the
# package without its dependencies installed, and the dependencies are
# specified in this file. distutils, a curse on your family even unto the
# seventh generation. Setuptools, that goes for you too - you had a chance to
# make this better, and you only made it worse.
with open('nsist/__init__.py', 'r') as f:
    for line in f:
        m = re.match(r"__version__ = (.+)$", line)
        if m:
            __version__ = eval(m.group(1))
            break

cmdclass = {}

class build_scripts_cmds(build_scripts):
    """Add <name>.cmd files so scripts work at the command line on Windows"""
    def copy_scripts(self):
        build_scripts.copy_scripts(self)
        for script in self.scripts:
            # XXX: Check that the file is a Python script?
            # (For now, assume that anything specified in scripts is Python)
            script_name = os.path.basename(script)
            cmd_file = os.path.join(self.build_dir, script_name + '.cmd')
            cmd = '"{python}" "%~dp0\{script}" %*\r\n'.format(
                    python=sys.executable, script=script_name)
            log.info("Writing %s wrapper script" % cmd_file)
            with open(cmd_file, 'w') as f:
                f.write(cmd)

if os.name == 'nt':
    cmdclass['build_scripts'] = build_scripts_cmds

setup(name='pynsist',
      version=__version__,
      description='Build Windows installers for Python apps',
      long_description=readme,
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://github.com/takluyver/pynsist',
      packages=['nsist'],
      package_data={'nsist': ['pyapp.nsi',
                              'pyapp_w_pylauncher.nsi',
                              'glossyorb.ico',
                             ]
                    },
      scripts=['scripts/pynsist'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Environment :: Win32 (MS Windows)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Software Distribution',
      ],
      install_requires=requirements,
      cmdclass=cmdclass,
)
