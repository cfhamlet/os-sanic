from collections import OrderedDict
from functools import partial
from inspect import isawaitable

from os_sanic.utils import NamedModel, load_class
from os_sanic.workflow import Workflowable


class ExtensionCfg(NamedModel):
    extension_class: str


class Extension(Workflowable):

    def __init__(self, application, config):
        self.application = application
        self.config = config
        self.logger = application.get_logger(config.name)

    @staticmethod
    def create(application, ext_cfg, user_cfg):
        config = ext_cfg.copy(update=user_cfg.copy(
            exclude=set(['extension_class'])).dict())

        package = None
        if config.extension_class.startswith('.'):
            package = application.app_cfg.package
        cls = load_class(config.extension_class, Extension, package=package)

        return cls(application, config)


class ExtensionManager(Workflowable):
    def __init__(self, application):
        self.application = application
        self.logger = application.get_logger(self.__class__.__name__)
        self._extensions = OrderedDict()
        self._load_extensions()
        [setattr(self, method, partial(self.__call, method))
         for method in ('setup', 'cleanup')]

    def _load_extensions(self):
        user_cfgs = dict([(cfg['name'], NamedModel(**cfg))
                          for cfg in self.application.user_cfg.EXTENSIONS if 'name' in cfg])

        for cfg in self.application.core_cfg.EXTENSIONS:
            try:
                ext_cfg = ExtensionCfg(**cfg)
                self._load_extension(
                    ext_cfg, user_cfgs.get(ext_cfg.name, ext_cfg))
            except Exception as e:
                self.logger.error(f'Load extension fail {e}, {ext_cfg}')

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
                self.logger.error(f'Extension error {key}.{method}, {e}')

    def _load_extension(self, ext_cfg, user_cfg):
        name = ext_cfg.name
        if name in self._extensions:
            self.logger.warn(f'Extension already exists, {name}')
            return
        extension = Extension.create(
            self.application, ext_cfg, user_cfg)
        self._extensions[name] = extension
        self.logger.debug(f'Load extension, {name} {extension.__class__}')
