import os
from enum import Enum
from logging import _nameToLevel
from typing import List, Union

from pydantic import BaseSettings, PositiveInt, ValidationError, validator
from sanic.config import Config


SANIC_ENV_PREFIX = 'OS_SANIC_'


class DefaultConfig(BaseSettings):

    LOGO: str = None

    DEBUG = False

    LOG_LEVEL: str = 'INFO'

    ACCESS_LOG = True

    KEEP_ALIVE = True

    HOST = '127.0.0.1'

    PORT: PositiveInt = 8001

    INSTALLED_APPS: List[Union[str, dict]] = []

    @validator('LOG_LEVEL')
    def valid_log_level(cls, v):
        if v.upper() not in _nameToLevel:
            raise ValidationError(f'Invalid log level {v}')
        return v

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
