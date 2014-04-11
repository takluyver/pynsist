#!/usr/bin/python3

import configparser

# contains all configuration sections and subsections
# the subsections are a tuple with their name and a boolean, which
# tells us whether the option is mandatory
VALID_CONFIG_SECTIONS = {
    'Application': [
        ('name', True),
        ('version', True),
        ('entry_point', True),
        ('script', False),
        ('icon', False),
        ('console', False),
    ],
    'Build': [
        ('directory', False),
        ('installer_name', False),
        ('nsi_template', False),
    ],
    'Include': [
        ('packages', False),
        ('files', False),
    ],
    'Python': [
        ('version', True),
        ('bitness', False),
    ],
}

class InvalidConfig(ValueError):
    pass

def read_and_validate(config_file):
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    # check mandatory sections
    for section_name, subsection_list in VALID_CONFIG_SECTIONS.items():
        for subsection_name, mandatory in subsection_list:
            if mandatory:
                try:
                    cfg[section_name][subsection_name]
                except KeyError:
                    err_msg = ("The section '{0}' must contain a "
                               "subsection '{1}'!").format(
                                section_name,
                                subsection_name)
                    raise InvalidConfig(err_msg)

    # check for invalid sections and subsections
    for section in cfg:
        # check section names
        section_name = str(section)
        is_valid_section_name = section_name in VALID_CONFIG_SECTIONS.keys()
        if section_name == 'DEFAULT':
            # DEFAULT is always inside the config, so just jump over it
            continue
        if not is_valid_section_name:
            err_msg = ("{0} is not a valid section header. Must "
                       "be one of these: {1}").format(
                       section_name, ', '.join(valid_section_headers))
            raise InvalidConfig(err_msg)
        # check subsection names
        for subsection in cfg[section_name]:
            subsection_name = str(subsection)
            subsection_names = [s[0] for s in VALID_CONFIG_SECTIONS[section_name]]
            is_valid_subsection = subsection_name in subsection_names
            if not is_valid_subsection:
                err_msg = ("'{0}' is not a valid subsection name for '{1}'. Must "
                           "be one of these: {2}").format(
                            subsection_name,
                            section_name,
                            ', '.join(subsection_names))
                raise InvalidConfig(err_msg)
    return cfg