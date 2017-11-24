import yaml
from . import VCLOUD_CONFIG_PATH

class Config(object):
    config = {}

    @classmethod
    def read(cls):
        with open(VCLOUD_CONFIG_PATH, 'r') as f:
            cls.config = yaml.load(f)['vcloud']
        return cls.config
