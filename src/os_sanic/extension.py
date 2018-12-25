from collections import OrderedDict

from os_config import Config
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class
from os_sanic.workflow import Workflowable


class Extension(Workflowable):

    def __init__(self, sanic, config):
        self._sanic = sanic
        self._config = config

    @property
    def name(self):
        return self._config.name


class ExtensionManager(Workflowable):
    def __init__(self, sanic):
        self._sanic = sanic
        self._extensions = OrderedDict()

    def run(self):
        list(map(lambda x: x.run(), self._extensions.values()))

    def setup(self):
        list(map(lambda x: x.setup(), self._extensions.values()))

    def cleanup(self):
        list(map(lambda x: x.cleanup(), reversed(self._extensions.values())))

    def load_extension(self, cfg, config):
        ec = cfg.extension_class
        c = Config.create()
        c.update(cfg)
        if config is not None:
            c.update(config)
        c.extension_class = ec
        cls = load_class(ec, Extension)

        extension = cls(self._sanic, c)
        self._extensions[extension.name] = extension

    @staticmethod
    def create(sanic, app_cfg, core, config):

        em = ExtensionManager(sanic)

        configs = {}
        for c in config.get('EXTENSIONS', []):
            name = c.get('name')
            if name:
                configs[name] = c

        for cfg in core.get('EXTENSIONS', []):
            name = cfg.get('name')
            if name:
                em.load_extension(cfg, configs.get(name))

        return em
