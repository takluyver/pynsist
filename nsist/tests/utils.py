import unittest
import sys

from os.path import isfile, isdir, exists, dirname

test_dir = dirname(__file__)

def assert_is_file(path):
    assert exists(path), "%s does not exist"
    assert isfile(path), "%s exists but is not a directory."

def assert_is_dir(path):
    assert exists(path), "%s does not exist"
    assert isdir(path), "%s exists but is not a directory."

def skip_on_windows(function):
    """Decorator to skip a test on Windows."""
    return unittest.skipIf(sys.platform.startswith("win"),
                           "Test for non-Windows platforms")(function)

def only_on_windows(function):
    """Decorator to skip a test on Windows."""
    return unittest.skipUnless(sys.platform.startswith("win"),
                               "Test requires Windows")(function)
