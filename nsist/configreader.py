#!/usr/bin/python3

import configparser

class SectionValidator(object):
    def __init__(self, keys):
        """
        keys
            list of tuples containing the names and whether the
            key is mandatory
        """
        self.keys = keys
    
    def check(self, config, section_name):
        """
        validates the section, if this is the correct validator for it
        returns True if this is the correct validator for this section
        
        raises InvalidConfig if something inside the section is wrong
        """
        self._check_mandatory_fields(section_name, config[section_name])
        self._check_invalid_keys(section_name, config[section_name])

    def _check_mandatory_fields(self, section_name, key):
        for key_name, mandatory in self.keys:
            if mandatory:
                try:
                    key[key_name]
                except KeyError:
                    err_msg = ("The section '{0}' must contain a "
                               "key '{1}'!").format(
                                section_name,
                                key_name)
                    raise InvalidConfig(err_msg)
    
    def _check_invalid_keys(self, section_name, section):
        for key in section:
            key_name = str(key)
            valid_key_names = [s[0] for s in self.keys]
            is_valid_key = key_name in valid_key_names
            if not is_valid_key:
                err_msg = ("'{0}' is not a valid key name for '{1}'. Must "
                           "be one of these: {2}").format(
                            key_name,
                            section_name,
                            ', '.join(valid_key_names))
                raise InvalidConfig(err_msg)

# contains all configuration sections and keys
# the keys are a tuple with their name and a boolean, which
# tells us whether the option is mandatory
CONFIG_VALIDATORS = {
    'Application': SectionValidator([
        ('name', True),
        ('version', True),
        ('entry_point', False),
        ('script', False),
        ('icon', False),
        ('console', False),
    ]),
    'Build': SectionValidator([
        ('directory', False),
        ('installer_name', False),
        ('nsi_template', False),
    ]),
    'Include': SectionValidator([
        ('packages', False),
        ('files', False),
    ]),
    'Python': SectionValidator([
        ('version', True),
        ('bitness', False),
    ]),
    'Shortcut': SectionValidator([
        ('entry_point', False),
        ('script', False),
        ('icon', False),
        ('console', False),
    ]),
}

class InvalidConfig(ValueError):
    pass

def read_and_validate(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    for section in config.sections():
        if section in CONFIG_VALIDATORS:
            CONFIG_VALIDATORS[section].check(config, section)
        elif section.startswith('Shortcut '):
            CONFIG_VALIDATORS['Shortcut'].check(config, section)
        else:
            valid_section_names = CONFIG_VALIDATORS.keys()
            err_msg = ("{0} is not a valid section header. Must "
                       "be one of these: {1}").format(
                       section,
                       ', '.join(['"%s"' % n for n in valid_section_names]))
            raise InvalidConfig(err_msg)    
    return config
