import sys
from distutils.core import setup

PY2 = sys.version_info[0] == 2
if PY2:
    requirements = [
        'configparser >= 3.3.0r2'
    ]
else:
    requirements = []

with open('README.rst', 'r') as f:
    readme=f.read()

from nsist import __version__

setup(name='pynsist',
      version=__version__,
      description='Build Windows installers for Python apps',
      long_description=readme,
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://github.com/takluyver/pynsist',
      packages=['nsist'],
      package_data={'nsist': ['template.nsi',
                              'python-pubkeys.txt',
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
