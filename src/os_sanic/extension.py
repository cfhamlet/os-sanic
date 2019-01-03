from collections import OrderedDict
from functools import partial
from inspect import isawaitable

from os_config import Config

from os_sanic.log import getLogger
from os_sanic.utils import load_class
from os_sanic.workflow import Workflowable


class Extension(Workflowable):

    def __init__(self, application, name, config):
        self.name = name
        self.application = application
        self.config = config

    @staticmethod
    def create(application, ext_cfg, user_config):
        ec = ext_cfg.extension_class
        config = Config.create()
        Config.update(config, ext_cfg)
        Config.update(config, user_config)
        name = Config.pop(config, 'name')
        Config.pop(config, 'extension_class')
        package = None
        if ec.startswith('.'):
            package = application.app_cfg.package
        cls = load_class(ec, Extension, package=package)
        return cls(application, name, config)


class ExtensionManager(Workflowable):
    def __init__(self, application):
        self.application = application
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
        iter = self._extensions.keys()
        if method == 'cleanup':
            iter = sorted(iter, reverse=True)

        for key in iter:
            ext = self._extensions[key]
            try:
                r = getattr(ext, method)()
                if isawaitable(r):
                    await r

            except Exception as e:
                self._logger.error(
                    'Extension error {}.{}, {}'.format(key, method, e))

    def load_extension(self, ext_cfg, user_config):

        try:
            name = ext_cfg.name
            if name in self._extensions:
                self._logger.warn(
                    'Extension already exists, {}'.format(name))
                return
            extension = Extension.create(
                self.application, ext_cfg, user_config)
            self._extensions[name] = extension
            self._logger.debug('Load extension, {} {}'.format(
                name, extension.__class__))
        except Exception as e:
            self._logger.error('Load extension fail {}, {}'.format(e, ext_cfg))

    @classmethod
    def create(cls, application):

        em = cls(application)

        user_configs = {}
        for cfg in Config.get(application.user_config, 'EXTENSIONS', []):
            name = Config.get(cfg, 'name')
            if name:
                user_configs[name] = cfg

        for ext_cfg in Config.get(application.core_config, 'EXTENSIONS', []):
            name = Config.get(ext_cfg, 'name')
            if name:
                em.load_extension(
                    ext_cfg, user_configs.get(name, Config.create()))

        return em
