import os
from collections import OrderedDict
from importlib import import_module

from os_config import Config

from os_sanic.extension import ExtensionManager
from os_sanic.view import ViewManager
from os_sanic.workflow import Workflowable


class Application(Workflowable):

    def __init__(self, sanic, cfg, core, config):
        self._sanic = sanic
        self._cfg = cfg
        self._core = core
        self._config = config
        self._ext_manager = ExtensionManager.create(sanic, cfg, core, config)
        ViewManager.load(sanic, cfg, core, config)

    @property
    def name(self):
        return self._cfg.name

    def setup(self):
        self._ext_manager.setup()

    def run(self):
        self._ext_manager.run()

    def cleanup(self):
        self._ext_manager.cleanup()

    @staticmethod
    def create(sanic, cfg):
        package = cfg.get('package')
        name = package.split('.')[-1]
        cfg.name = cfg.get('name', name)

        app_module = import_module('.'.join((package, 'app')))
        core = Config.from_object(app_module)
        config = Config.create()
        if cfg.get('config'):
            f = os.path.join(os.getcwd(), cfg.config)
            config = Config.from_pyfile(f)

        return Application(sanic, cfg, core, config)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self._sanic = sanic
        self._apps = OrderedDict()

    def load_app(self, cfg):
        app = Application.create(self._sanic, cfg)
        self._apps[app.name] = app

    def run(self):
        list(map(lambda x: x.run(), self._apps.values()))

    def setup(self):
        list(map(lambda x: x.setup(), self._apps.values()))

    def cleaup(self):
        list(map(lambda x: x.cleanup(), reversed(self._apps.values())))

    @staticmethod
    def create(sanic):

        am = ApplicationManager(sanic)
        for cfg in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(cfg)
        return am
