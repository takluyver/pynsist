#!/usr/bin/python3

import configparser

class SectionValidator(object):
    def __init__(self, name, subsections, identification_func=None):
        """
        name
            a descriptive name of the section
        subsections
            list of tuples containing the names and whether the
            subsection is mandatory
        identy_func
            returns True if this is the correct Validator for the
            section name. If it is left out the descriptive name will be
            used to identify the section
        """
        self.name = name
        self.identification_func = identification_func
        self.subsections = subsections
    
    def check(self, config, section_name):
        """
        validates the section, if this is the correct validator for it
        returns True if this is the correct validator for this section
        
        raises InvalidConfig if something inside the section is wrong
        """
        was_identified = False        
        if self._identify(section_name):
            was_identified = True
            self._check_mandatory_fields(section_name, config[section_name])
            self._check_invalid_subsections(section_name, config[section_name])
        return was_identified

    def _identify(self, section_name):
        # if no identification function is set, just compare the section
        # name with the name of the validator
        if self.identification_func is None:
            return section_name == self.name
        else:
            return self.identification_func(section_name)

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
        # check subsection names
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
CONFIG_VALIDATORS = [
    SectionValidator('Application',
        [
            ('name', True),
            ('version', True),
            ('entry_point', True),
            ('script', False),
            ('icon', False),
            ('console', False),
        ],
    ),
    SectionValidator('Build',
        [
            ('directory', False),
            ('installer_name', False),
            ('nsi_template', False),
        ]
    ),
    SectionValidator('Include',
        [
            ('packages', False),
            ('files', False),
        ]
    ),
    SectionValidator('Python',
        [
            ('version', True),
            ('bitness', False),
        ]
    ),
]

class InvalidConfig(ValueError):
    pass

def read_and_validate(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    for section in config.sections():
        # each section *must* be identified by at least one validator
        # otherwise it is an invalid section (e.g. has an invalid name)
        was_identified = False
        for validator in CONFIG_VALIDATORS:
            was_identified = validator.check(config, section)
            # if we already found the correct validator and it did not
            # raise InvalidConfig, we can skip the other validators
            if was_identified:
                break
        if not was_identified:
            valid_section_names = [v.name for v in CONFIG_VALIDATORS]
            err_msg = ("{0} is not a valid section header. Must "
                       "be one of these: {1}").format(
                       section,
                       ', '.join(['"%s"' % n for n in valid_section_names]))
            raise InvalidConfig(err_msg)    
    return config
