import os
import nsist

example_cfgs = [
    'console/installer.cfg',
    'pyqt/installer.cfg',
    'tkinter/installer.cfg',
    'pygame/installer.cfg',
    'pygtk/installer.cfg',
    'pygtk_mpl_numpy/installer.cfg',
    'pygi_mpl_numpy/installer.cfg',
]

examples_dir = os.path.dirname(os.path.abspath(__file__))

for example_cfg in example_cfgs:
    os.chdir(examples_dir)
    nsist.main([example_cfg])
