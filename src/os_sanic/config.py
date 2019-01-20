import os
from typing import List, Union

from pydantic import BaseSettings, PositiveInt
from sanic.config import Config

from os_sanic.utils import LogLevel

SANIC_ENV_PREFIX = 'OS_SANIC_'


class DefaultConfig(BaseSettings):

    LOGO: str = None

    DEBUG = False

    LOG_LEVEL: LogLevel = 'INFO'

    ACCESS_LOG = True

    KEEP_ALIVE = True

    HOST = '127.0.0.1'

    PORT: PositiveInt = 8001

    INSTALLED_APPS: List[Union[str, dict]] = []

    class Config:
        env_prefix = SANIC_ENV_PREFIX
        ignore_extra = True


def create(params=None, load_env=True):
    config = Config(load_env=False)
    config.update(dict([(k, v.default)
                        for k, v in DefaultConfig.__fields__.items()]))

    if load_env:
        if isinstance(load_env, bool):
            load_env = SANIC_ENV_PREFIX
        config.load_environment_vars(prefix=load_env)

    if params:
        config.update(params)
    DefaultConfig.validate(config)
    return config
