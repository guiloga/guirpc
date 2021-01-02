import os
import yaml


def read_config_defaults():
    filepath = os.path.join(os.path.dirname(__file__),
                            'config_defaults.yaml')
    with open(filepath, 'r') as file:
        cd = yaml.safe_load(file)

    return cd
