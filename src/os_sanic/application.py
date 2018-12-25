import os

from collections import OrderedDict
from importlib import import_module

from os_config import Config
from os_sanic.extension import ExtensionManager
from os_sanic.handler import HandlerManager


class Application(object):

    def __init__(self, sanic, name, core, config):
        self._sanic = sanic
        self._core = core
        self._config = config
        self.name = name
        self._ext_manager = ExtensionManager.create(
            sanic, core.get('EXTENSIONS', []), config.get('EXTENSIONS', []))
        self._handle_manager = HandlerManager.create(
            sanic, core.get('HANDLERS', []), config.get('HANDLERS', []))

    @staticmethod
    def create(sanic, config):
        package = config.get('package')
        name = package.split('.')[-1]
        name = config.get('namespace', name)
        app_module = import_module('.'.join((package, 'app')))
        app_core = Config.from_object(app_module)
        app_config = None
        if app_core.get('config'):
            f = os.path.join(os.getcwd(), app_core.config)
            app_config = Config.from_pyfile(f)

        return Application(sanic, name, app_core, app_config)


class ApplicationManager(object):

    def __init__(self, sanic):
        self._sanic = sanic
        self._apps = OrderedDict()

    def load_app(self, app_config):
        app = Application.create(self._sanic, app_config)
        self._apps[app.name] = app

    @staticmethod
    def create(sanic):

        am = ApplicationManager(sanic)
        for config in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(config)
        return am
