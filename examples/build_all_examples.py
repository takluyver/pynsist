import os
import nsist

example_cfgs = [
    'console/installer.cfg',
    'pyqt/installer.cfg',
    'tkinter/installer.cfg',
    'pygame/installer.cfg',
]

examples_dir = os.path.dirname(os.path.abspath(__file__))

for example_cfg in example_cfgs:
    os.chdir(examples_dir)
    nsist.main([example_cfg])
