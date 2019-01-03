import inspect
import os

from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.log import LOGGING_CONFIG_PATCH, logger
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
        self.app_manager = ApplicationManager.create(self.sanic)

        @self.sanic.listener('before_server_start')
        async def setup(app, loop):
            await self.setup()

        @self.sanic.listener('after_server_stop')
        async def cleanup(app, loop):
            await self.cleanup()

        @self.sanic.listener('after_server_start')
        async def run(app, loop):
            await self.app_manager.run()

    async def setup(self):
        await self.app_manager.setup()

    async def cleanup(self):
        await self.app_manager.cleanup()

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

    @classmethod
    def create(cls, name, config_file=None, env_prefix=SANIC_ENV_PREFIX,
               log_config=None, **kwargs):
        sanic_config = create_sanic_config(load_env=env_prefix)
        if config_file:
            sanic_config.from_pyfile(config_file)
        return cls(name, sanic_config, log_config, **kwargs)
