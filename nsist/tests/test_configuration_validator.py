from nose.tools import *
import os
from .. import configreader
import configparser

DATA_FILES = os.path.join(os.path.dirname(__file__), 'data_files')

def test_valid_config():
    configfile = os.path.join(DATA_FILES, 'valid_config.cfg')
    configreader.read_and_validate(configfile)

@raises(configreader.InvalidConfig)
def test_invalid_config_keys():
    configfile = os.path.join(DATA_FILES, 'invalid_config_keys.cfg')
    configreader.read_and_validate(configfile)

@raises(configreader.InvalidConfig)
def test_invalid_config_subsection():
    configfile = os.path.join(DATA_FILES, 'invalid_config_subsection.cfg')
    configreader.read_and_validate(configfile)

@raises(configreader.InvalidConfig)
def test_missing_config_subsection():
    configfile = os.path.join(DATA_FILES, 'missing_config_subsection.cfg')
    configreader.read_and_validate(configfile)

@raises(configparser.Error)
def test_invalid_config_file():
    configfile = os.path.join(DATA_FILES, 'not_a_config.cfg')
    configreader.read_and_validate(configfile)
