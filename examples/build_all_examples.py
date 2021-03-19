import os
import nsist

example_cfgs = [
    'console/installer.cfg',
    'pygame/installer.cfg',
    # 'pygi_mpl_numpy/installer.cfg',  # this example does not currently work
    'pyglet/installer.cfg',
    'pyqt5/installer.cfg',
    'pyqt5_opencv/installer.cfg',
    'pyqt5_qml/installer.cfg',
    'pywebview/installer.cfg',
]

examples_dir = os.path.dirname(os.path.abspath(__file__))

for example_cfg in example_cfgs:
    os.chdir(examples_dir)
    nsist.main([example_cfg])
