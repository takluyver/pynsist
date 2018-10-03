import unittest
import sys

from os.path import dirname

test_dir = dirname(__file__)


def skip_on_windows(function):
    """Decorator to skip a test on Windows."""
    return unittest.skipIf(sys.platform.startswith("win"),
                           "Test for non-Windows platforms")(function)

def only_on_windows(function):
    """Decorator to skip a test on Windows."""
    return unittest.skipUnless(sys.platform.startswith("win"),
                               "Test requires Windows")(function)
