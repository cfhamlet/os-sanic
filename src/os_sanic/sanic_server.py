import inspect

from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS, logger

from os_sanic.application import ApplicationManager
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.utils import deep_update
from os_sanic.workflow import Workflowable

LOGGIN_CONFIG_PATCH = dict(

    formatters={
        "generic": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
        },
    }
)


class Server(Workflowable):
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

        @self._sanic.listener('before_server_start')
        def setup(app, loop):
            self.setup()

        @self._sanic.listener('after_server_stop')
        def cleanup(app, loop):
            self.cleanup()

        @self._sanic.listener('after_server_start')
        def run(app, loop):
            self._app_manager.run()

    def setup(self):
        self._app_manager.setup()

    def cleanup(self):
        self._app_manager.cleaup()

    def _run_args(self):
        argspec = inspect.getargspec(self._sanic.run)
        run_args = {}
        offset = len(argspec.args)-len(argspec.defaults)
        for idx in range(len(argspec.defaults)-1, -1, -1):
            default = argspec.defaults[idx]
            idx += offset
            name = argspec.args[idx]
            run_args[name] = self._sanic.config.get(name.upper(), default)

        return run_args

    def run(self):
        self._sanic.run(**self._run_args())

    @staticmethod
    def create(name, config_file=None, env_prefix=SANIC_ENV_PREFIX,
               log_config=None, **kwargs):
        config = create_sanic_config(load_env=env_prefix)
        if config_file:
            config.from_pyfile(config_file)
        return Server(name, config, log_config, **kwargs)
