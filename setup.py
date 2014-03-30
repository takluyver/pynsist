from distutils.core import setup

setup(name='pynsis',
      version='0.1',
      description='Build Windows installers for Python apps',
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://github.com/takluyver/pynsis',
      packages=['nsisbuilder'],
      package_data={'nsisbuilder': ['template.nsi',
                                    'python-pubkeys.txt',
                                    'glossyorb.ico',
                                    ]
                    },
      scripts=['scripts/pynsis'],
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