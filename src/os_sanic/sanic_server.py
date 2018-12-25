from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS, logger

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.utils import deep_update

LOGGIN_CONFIG_PATCH = dict(

    formatters={
        "generic": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
        },
    }
)


class Server(object):
    def __init__(self, name, config, log_config=None, **kwargs):
        if not log_config:
            log_config = deep_update({}, LOGGING_CONFIG_DEFAULTS)
            deep_update(log_config, LOGGIN_CONFIG_PATCH)

        self._sanic = Sanic(name=name, log_config=log_config)
        self._sanic.config = config
        self._sanic.config.update(kwargs)
        logger.setLevel(self._sanic.config.LOG_LEVEL)
        logger.debug('Config: {}'.format(self._sanic.config))
        self._app_manager = ApplicationManager.create(self._sanic)

    def run(self):
        config = self._sanic.config
        self._sanic.run(host=config.HOST, port=config.PORT,
                        debug=config.DEBUG, access_log=config.ACCESS_LOG)

    @staticmethod
    def create(name, config_file=None, env_prefix=SANIC_ENV_PREFIX,
               log_config=None, **kwargs):
        config = create_sanic_config(load_env=env_prefix)
        if config_file:
            config.from_pyfile(config_file)
        return Server(name, config, log_config, **kwargs)
