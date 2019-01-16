import inspect
import logging
import os
from functools import partial

from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.log import LOGGING_CONFIG_PATCH, logger
from os_sanic.utils import deep_update
from os_sanic.monkey_patch import patch


class Server(object):
    def __init__(self, app_manager, enable_workflow=True):
        self.app_manager = app_manager
        if enable_workflow:
            self.__register_workflow()

    def __register_workflow(self):
        [self.sanic.register_listener(partial(self.__call, method), event)
         for method, event in zip(('run', 'setup', 'cleanup'),
                                  ('before_server_start',
                                   'after_server_start',
                                   'after_server_stop'))]

    @property
    def sanic(self):
        return self.app_manager.sanic

    async def __call(self, method, app, loop):
        await getattr(self.app_manager, method)()

    def _run_args(self):
        argspec = inspect.getargspec(self.sanic.run)
        run_args = {}
        offset = len(argspec.args)-len(argspec.defaults)
        for idx in range(len(argspec.defaults)-1, -1, -1):
            default = argspec.defaults[idx]
            idx += offset
            name = argspec.args[idx]
            run_args[name] = self.sanic.config.get(name.upper(), default)

        return run_args

    def run(self):
        with patch():
            self.sanic.run(**self._run_args())

    @classmethod
    def create(cls, app='os-sanic', config=None, env_prefix=SANIC_ENV_PREFIX, log_config=None):

        assert isinstance(app, (str, Sanic))

        if isinstance(app, str):
            app = Sanic(app, load_env=env_prefix)

        conf = create_sanic_config(load_env=env_prefix)
        if config:
            conf.update(config)

        app.config.update(conf)

        if app.configure_logging:
            if not log_config:
                log_config = deep_update({}, LOGGING_CONFIG_DEFAULTS)
                deep_update(log_config, LOGGING_CONFIG_PATCH)
            logging.config.dictConfig(log_config)

        if app.config.get('DEBUG', False):
            if os.environ.get('SANIC_SERVER_RUNNING') != 'true':
                return cls(ApplicationManager.create(app), False)

            logger.setLevel('DEBUG')
            logger.debug('Debug mode')
        else:
            logger.setLevel(app.config.LOG_LEVEL)

        logger.debug(f'Config: {app.config}')

        return cls(ApplicationManager.create(app))
