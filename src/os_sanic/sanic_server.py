import os
import inspect

from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS
from os_sanic.log import logger, LOGGING_CONFIG_PATCH

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.utils import deep_update
from os_sanic.workflow import Workflowable


class Server(Workflowable):
    def __init__(self, name, config, log_config=None, **kwargs):
        if not log_config:
            log_config = deep_update({}, LOGGING_CONFIG_DEFAULTS)
            deep_update(log_config, LOGGING_CONFIG_PATCH)

        self.sanic = Sanic(name=name, log_config=log_config)
        self.sanic.config = config
        self.sanic.config.update(kwargs)
        if self.sanic.config.get("DEBUG", False):
            if os.environ.get('SANIC_SERVER_RUNNING') != 'true':
                return
            logger.setLevel('DEBUG')
            logger.debug('Debug mode')
        else:
            logger.setLevel(self.sanic.config.LOG_LEVEL)
        logger.debug('Config: {}'.format(self.sanic.config))
        self._app_manager = ApplicationManager.create(self.sanic)

        @self.sanic.listener('before_server_start')
        def setup(app, loop):
            self.setup()

        @self.sanic.listener('after_server_stop')
        def cleanup(app, loop):
            self.cleanup()

        @self.sanic.listener('after_server_start')
        def run(app, loop):
            self._app_manager.run()

    def setup(self):
        self._app_manager.setup()

    def cleanup(self):
        self._app_manager.cleanup()

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
        self.sanic.run(**self._run_args())

    @staticmethod
    def create(name, config_file=None, env_prefix=SANIC_ENV_PREFIX,
               log_config=None, **kwargs):
        sanic_config = create_sanic_config(load_env=env_prefix)
        if config_file:
            sanic_config.from_pyfile(config_file)
        return Server(name, sanic_config, log_config, **kwargs)
