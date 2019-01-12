import os
from os_sanic.utils import deep_update
from sanic.config import Config

SANIC_ENV_PREFIX = 'OS_SANIC_'


def create_sanic_config(defaults=None, load_env=True, keep_alive=True):
    default = SanicConfig(defaults, False, keep_alive=keep_alive)
    default_config_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'default_config.py')
    default.from_pyfile(default_config_file)
    if not load_env:
        return default

    return SanicConfig(default, load_env, default.KEEP_ALIVE)


class SanicConfig(Config):

    def __init__(self, defaults=None, load_env=True, keep_alive=True):
        super(SanicConfig, self).__init__(defaults=defaults,
                                          load_env=load_env,
                                          keep_alive=keep_alive)
        self.LOGO = None
