from nose.tools import *
import os
from nsist import read_and_verify_config_file

DATA_FILES = os.path.join(os.path.dirname(__file__), 'data_files')

def test_valid_config():
    configfile = os.path.join(DATA_FILES, 'valid_config.cfg')
    read_and_verify_config_file(configfile)

@raises(NameError)
def test_invalid_config_keys():
    configfile = os.path.join(DATA_FILES, 'invalid_config_keys.cfg')
    read_and_verify_config_file(configfile)

@raises(NameError)
def test_invalid_config_subsection():
    configfile = os.path.join(DATA_FILES, 'invalid_config_subsection.cfg')
    read_and_verify_config_file(configfile)

@raises(NameError)
def test_missing_config_subsection():
    configfile = os.path.join(DATA_FILES, 'missing_config_subsection.cfg')
    read_and_verify_config_file(configfile)

@raises(Exception)
def test_invalid_config_file():
    configfile = os.path.join(DATA_FILES, 'not_a_config.cfg')
    read_and_verify_config_file(configfile)
