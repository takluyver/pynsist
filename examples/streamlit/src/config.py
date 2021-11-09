import os


class EnvironmentalVariableNames:
    """ Defines the names of the environmental variables used in the code and useful shortcuts"""

    # Environmental variables
    WORKING_DIR = "WORKING_DIR"


def get_env(env_var):
    """ Returns the value of the environment variable env_var """
    return os.environ[env_var]
