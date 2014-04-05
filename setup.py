from distutils.core import setup

with open('README.rst', 'r') as f:
    readme=f.read()

setup(name='pynsist',
      version='0.1',
      description='Build Windows installers for Python apps',
      long_description=readme,
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://github.com/takluyver/pynsis',
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
          'Topic :: Software Development',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Software Distribution',
      ]
)
