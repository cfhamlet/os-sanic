import inspect
import os
from functools import partial

from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.log import LOGGING_CONFIG_PATCH, logger
from os_sanic.utils import deep_update


class Server(object):
    def __init__(self, app_manager):
        self.app_manager = app_manager
        [self.sanic.register_listener(partial(self.__call, method), event)
         for method, event in zip(('run', 'setup', 'cleanup'),
                                  ('before_server_start',
                                   'after_server_start',
                                   'after_server_stop'))]

    @property
    def sanic(self):
        return self.app_manager.sanic

    async def __call(self, method, app, loop):
        getattr(self.app_manager, method)()

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
    def create(cls, app='os-sanic', config=None, log_config=None, **kwargs):

        assert isinstance(app, (str, Sanic))
        if isinstance(app, str):
            app = Sanic(app)

        return cls(ApplicationManager.create(app))
