"""Script to remove build/ directories from all examples.
"""
import os, shutil

examples_dir = os.path.dirname(os.path.abspath(__file__))

for d in os.listdir('.'):
    build_dir = os.path.join(examples_dir, d, 'build')
    if os.path.isdir(build_dir):
        print("Removing {}/build".format(d))
        shutil.rmtree(build_dir)
