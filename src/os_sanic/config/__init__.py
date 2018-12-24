import os
from os_sanic.utils import deep_update
from sanic.config import Config as SanicConfig


def create_config(defaults=None, load_env=True):
    default = Config(defaults, load_env)
    default_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'default_config.py')
    default.from_pyfile(default_config_file)
    if not load_env:
        return default
    return Config(default, load_env, default.KEEP_ALIVE)


class Config(SanicConfig):

    def __init__(self, defaults=None, load_env=True, keep_alive=True):
        super(Config, self).__init__(defaults=defaults,
                                     load_env=load_env,
                                     keep_alive=keep_alive)
        self.LOGO = None
