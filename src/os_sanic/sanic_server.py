from sanic import Sanic
from sanic.log import logger

from os_sanic.config import create_config
from os_sanic.utils import deep_update

LOGGIN_CONFIG_PATCH = dict(

    formatters={
        "generic": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
        },
    }
)

ENV_PREFIX = 'OS_SANIC_'


class Server(object):
    def __init__(self, name, config, log_config=None, **kwargs):
        if not log_config:
            log_config = deep_update({}, LOGGIN_CONFIG_PATCH)
        self._app = Sanic(name=name, log_config=log_config)
        self._app.config = config
        self._app.config.update(kwargs)
        logger.setLevel(self._app.config.LOG_LEVEL)
        logger.debug('Config: {c}'.format(self._app.config))

    def run(self):
        pass

    @staticmethod
    def create(name, config_file=None, env_prefix=ENV_PREFIX,
               log_config=None, **kwargs):
        config = create_config(load_env=env_prefix)
        if config_file:
            config.from_pyfile(config_file)
        return Server(name, config, log_config, **kwargs)
