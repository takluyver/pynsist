#!/usr/bin/python3

import configparser
import os.path
from pathlib import Path

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
        ('publisher', False),
        ('entry_point', False),
        ('script', False),
        ('target', False),
        ('parameters', False),
        ('icon', False),
        ('console', False),
        ('extra_preamble', False),
        ('license_file', False),
    ]),
    'Build': SectionValidator([
        ('directory', False),
        ('installer_name', False),
        ('nsi_template', False),
    ]),
    'Include': SectionValidator([
        ('packages', False),
        ('pypi_wheels', False),
        ('extra_wheel_sources', False),
        ('files', False),
        ('exclude', False),
        ('local_wheels', False)
    ]),
    'Python': SectionValidator([
        ('version', False),
        ('bitness', False),
        ('format', False),
        ('include_msvcrt', False),
    ]),
    'Shortcut': SectionValidator([
        ('entry_point', False),
        ('script', False),
        ('target', False),
        ('parameters', False),
        ('icon', False),
        ('console', False),
        ('extra_preamble', False),
    ]),
    'Command': SectionValidator([
        ('entry_point', True),
        ('console', False),
        ('extra_preamble', False),
    ])
}

class InvalidConfig(ValueError):
    pass

def read_and_validate(config_file):
    # Interpolation interferes with Windows-style environment variables, so
    # it's disabled for now.
    config = configparser.ConfigParser(interpolation=None)
    if config.read(config_file) == []:
        raise InvalidConfig("Config file not found: %r" % config_file)
    for section in config.sections():
        if section in CONFIG_VALIDATORS:
            CONFIG_VALIDATORS[section].check(config, section)
        elif section.startswith('Shortcut '):
            CONFIG_VALIDATORS['Shortcut'].check(config, section)
        elif section.startswith('Command '):
            CONFIG_VALIDATORS['Command'].check(config, section)
        else:
            valid_section_names = CONFIG_VALIDATORS.keys()
            err_msg = ("{0} is not a valid section header. Must "
                       "be one of these: {1}").format(
                       section,
                       ', '.join(['"%s"' % n for n in valid_section_names]))
            raise InvalidConfig(err_msg)
    return config

def read_extra_files(cfg):
    """Read the list of extra files from the config file.

    Returns a list of 2-tuples: (file, destination_directory), which can be
    passed as the ``extra_files`` parameter to :class:`nsist.InstallerBuilder`.
    """
    lines = cfg.get('Include', 'files', fallback='').splitlines()
    pairs = []
    for line in lines:
        if '>' in line:
            file, dest = line.rsplit('>', 1)
            pairs.append((file.strip(), dest.strip()))
        else:
            pairs.append((line, '$INSTDIR'))

    return pairs

def read_shortcuts_config(cfg):
    """Read and verify the shortcut definitions from the config file.

    There is one shortcut per 'Shortcut <name>' section, and one for the
    Application section.

    Returns a dict of dicts with the fields from the shortcut sections.
    The optional 'icon' and 'console' fields will be filled with their
    default values if not supplied.
    """
    shortcuts = {}
    def _check_shortcut(name, sc, section):
        alternatives = ['entry_point', 'script', 'target']
        has_alternatives = sum(1 for k in alternatives if k in sc)
        if has_alternatives < 1:
            raise InvalidConfig('Section [{}] has none of {}.'.format(
                                    section, ', '.join(alternatives)))
        elif has_alternatives > 1:
            raise InvalidConfig('Section [{}] has more than one of {}.'.format(
                                    section, ', '.join(alternatives)))

        # Copy to a regular dict so it can hold a boolean value
        sc2 = dict(sc)
        if 'icon' not in sc2:
            from . import DEFAULT_ICON
            sc2['icon'] = DEFAULT_ICON
        sc2['console'] = sc.getboolean('console', fallback=False)
        sc2['parameters'] = sc.get('parameters', fallback='')
        if 'extra_preamble' in sc2:
            if 'entry_point' not in sc2:
                raise InvalidConfig('extra_preamble is only valid with entry_point')
            preamb_file = sc2['extra_preamble']
            if not os.path.isfile(preamb_file):
                raise InvalidConfig('extra_preamble file %r does not exist' %
                                                    preamb_file)

        shortcuts[name] = sc2

    for section in cfg.sections():
        if section.startswith("Shortcut "):
            name = section[len("Shortcut "):]
            _check_shortcut(name, cfg[section], section)

    appcfg = cfg['Application']
    _check_shortcut(appcfg['name'], appcfg, 'Application')

    return shortcuts

def read_commands_config(cfg):
    """Read and verify the command definitions from the config file.

    Returns a dict of dicts, keyed by command name, containing the values from
    the command sections of the config file.
    """
    commands = {}
    for section in cfg.sections():
        if section.startswith("Command "):
            name = section[len("Command "):]
            commands[name] = cc = dict(cfg[section])
            cc['console'] = cfg[section].getboolean('console', fallback=True)
            if ('extra_preamble' in cc) and \
                    not os.path.isfile(cc['extra_preamble']):
                raise InvalidConfig('extra_preamble file %r does not exist' %
                                    cc['extra_preamble'])

    return commands


def get_installer_builder_args(config):
    from . import (DEFAULT_BITNESS,
                    DEFAULT_BUILD_DIR,
                    DEFAULT_ICON,
                    DEFAULT_PY_VERSION)

    appcfg = config['Application']
    args = {}
    args['appname'] = appcfg['name']
    args['version'] = appcfg['version']
    args['shortcuts'] = read_shortcuts_config(config)
    args['commands'] = read_commands_config(config)
    args['publisher'] = appcfg.get('publisher', None)
    args['icon'] = appcfg.get('icon', DEFAULT_ICON)
    args['license_file'] = appcfg.get('license_file', None)
    args['packages'] = config.get('Include', 'packages', fallback='').strip().splitlines()
    args['pypi_wheel_reqs'] = config.get('Include', 'pypi_wheels', fallback='').strip().splitlines()
    args['extra_wheel_sources'] = [Path(p) for p in
        config.get('Include', 'extra_wheel_sources', fallback='').strip().splitlines()
    ]
    args['extra_files'] = read_extra_files(config)
    args['py_version'] = config.get('Python', 'version', fallback=DEFAULT_PY_VERSION)
    args['py_bitness'] = config.getint('Python', 'bitness', fallback=DEFAULT_BITNESS)
    args['inc_msvcrt'] = config.getboolean('Python', 'include_msvcrt', fallback=True)
    args['build_dir'] = config.get('Build', 'directory', fallback=DEFAULT_BUILD_DIR)
    args['installer_name'] = config.get('Build', 'installer_name', fallback=None)
    args['nsi_template'] = config.get('Build', 'nsi_template', fallback=None)
    args['exclude'] = config.get('Include', 'exclude', fallback='').strip().splitlines()
    args['local_wheels'] = config.get('Include', 'local_wheels', fallback='').strip().splitlines()
    return args
