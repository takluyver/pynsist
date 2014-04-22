import re
import sys
from distutils.core import setup

PY2 = sys.version_info[0] == 2

requirements = ['requests',
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

setup(name='pynsist',
      version=__version__,
      description='Build Windows installers for Python apps',
      long_description=readme,
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://github.com/takluyver/pynsist',
      packages=['nsist'],
      package_data={'nsist': ['template.nsi',
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
      install_requires=requirements
)
