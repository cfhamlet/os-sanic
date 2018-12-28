from inspect import isawaitable
from collections import OrderedDict
from functools import partial

from os_config import Config
from sanic.views import HTTPMethodView

from os_sanic.log import getLogger, logger
from os_sanic.utils import load_class
from os_sanic.workflow import Workflowable


class Extension(Workflowable):

    def __init__(self, sanic, config):
        self.sanic = sanic
        self.config = config

    @staticmethod
    def create(sanic, app_cfg, ext_cfg, user_config):
        ec = ext_cfg.extension_class
        config = Config.create()
        Config.update(config, ext_cfg)
        if user_config is not None:
            Config.update(config, user_config)
        config.extension_class = ec
        package = None
        if ec.startswith('.'):
            package = app_cfg.package
        cls = load_class(ec, Extension, package=package)
        return cls(sanic, config)


class ExtensionManager(Workflowable):
    def __init__(self, app_manager):
        self._extensions = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)
        [setattr(self, m, partial(self.__call, m))
         for m in ('run', 'setup', 'cleanup')]

    def get_extension(self, name):
        return self._extensions[name]

    @property
    def extensions(self):
        return self._extensions.values()

    async def __call(self, method):
        for key, ext in self._extensions.items():
            try:
                r = getattr(ext, method)()
                if isawaitable(r):
                    await r

            except Exception as e:
                self._logger.error(
                    'Extension error {}.{}, {}'.format(key, method, e))

    def load_extension(self, app_cfg, ext_cfg, user_config):

        try:
            name = ext_cfg.name
            if name in self._extensions:
                self._logger.warn(
                    'Extension already exists, {}'.format(name))
                return
            extension = Extension.create(
                self._sanic, app_cfg, ext_cfg, user_config)
            self._extensions[name] = extension
            self._logger.debug('Load extension, {} {}'.format(
                name, extension.__class__))
        except Exception as e:
            self._logger.error('Load extension fail {}, {}'.format(e, ext_cfg))

    @staticmethod
    def create(app_manager):

        em = ExtensionManager(app_manager)

        user_configs = {}
        for cfg in Config.get(app_manager.user_config, 'EXTENSIONS', []):
            name = Config.get(cfg, 'name')
            if name:
                user_configs[name] = cfg

        for ext_cfg in Config.get(app_manager.core_config, 'EXTENSIONS', []):
            name = Config.get(ext_cfg, 'name')
            if name:
                em.load_extension(ext_cfg, user_configs.get(name))

        return em
