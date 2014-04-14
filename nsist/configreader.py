#!/usr/bin/python3

import configparser

class SectionValidator(object):
    def __init__(self, subsections):
        """
        subsections
            list of tuples containing the names and whether the
            subsection is mandatory
        """
        self.subsections = subsections
    
    def check(self, config, section_name):
        """
        validates the section, if this is the correct validator for it
        returns True if this is the correct validator for this section
        
        raises InvalidConfig if something inside the section is wrong
        """
        self._check_mandatory_fields(section_name, config[section_name])
        self._check_invalid_subsections(section_name, config[section_name])

    def _check_mandatory_fields(self, section_name, subsection):
        for subsection_name, mandatory in self.subsections:
            if mandatory:
                try:
                    subsection[subsection_name]
                except KeyError:
                    err_msg = ("The section '{0}' must contain a "
                               "subsection '{1}'!").format(
                                section_name,
                                subsection_name)
                    raise InvalidConfig(err_msg)
    
    def _check_invalid_subsections(self, section_name, section):
        for subsection in section:
            subsection_name = str(subsection)
            valid_subsection_names = [s[0] for s in self.subsections]
            is_valid_subsection = subsection_name in valid_subsection_names
            if not is_valid_subsection:
                err_msg = ("'{0}' is not a valid subsection name for '{1}'. Must "
                           "be one of these: {2}").format(
                            subsection_name,
                            section_name,
                            ', '.join(valid_subsection_names))
                raise InvalidConfig(err_msg)

# contains all configuration sections and subsections
# the subsections are a tuple with their name and a boolean, which
# tells us whether the option is mandatory
CONFIG_VALIDATORS = {
    'Application': SectionValidator([
        ('name', True),
        ('version', True),
        ('entry_point', True),
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
