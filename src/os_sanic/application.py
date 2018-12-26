import os
from collections import OrderedDict
from importlib import import_module

from os_config import Config

from os_sanic.extension import ExtensionManager
from os_sanic.log import getLogger
from os_sanic.view import ViewManager
from os_sanic.workflow import Workflowable


class Application(Workflowable):

    def __init__(self, sanic, name, app_cfg, core_config, user_config):
        self._sanic = sanic
        self.name = name
        self._app_cfg = app_cfg
        self._ext_manager = ExtensionManager.create(
            sanic, app_cfg, core_config, user_config)
        ViewManager.load(sanic, name, app_cfg, core_config, user_config)
        [setattr(self, m, lambda _: getattr(self._ext_manager, m)())
         for m in ('setup', 'run', 'cleanup')]

    @staticmethod
    def create(sanic, name, app_cfg):

        app_module = import_module('.'.join((app_cfg.package, 'app')))
        core_config = Config.from_object(app_module)
        user_config = Config.create()
        if app_cfg.get('config'):
            f = os.path.join(os.getcwd(), app_cfg.config)
            user_config = Config.from_pyfile(f)

        return Application(sanic, name, app_cfg, core_config, user_config)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self._sanic = sanic
        self._apps = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)

    def load_app(self, app_cfg):
        try:
            if isinstance(app_cfg, str):
                app_cfg = Config.create(package=app_cfg)
            if not app_cfg.get('package'):
                self._logger.warn(
                    'Load app skip, no package {}'.format(app_cfg))
                return

            name = app_cfg.package.split('.')[-1]
            name = app_cfg.get('name', name)
            if name in self._apps:
                self._logger.warn('App already exists, {}'.format(name))
                return

            self._logger.debug(
                'Load app, {} {}'.format(name, app_cfg.package))
            app = Application.create(self._sanic, name, app_cfg)
            self._apps[name] = app
        except Exception as e:
            self._logger.error('Load app fail, {}, {}'.format(e, app_cfg))

    def run(self):
        [x.run(self) for x in self._apps.values()]

    def setup(self):
        [x.setup(self) for x in self._apps.values()]

    def cleanup(self):
        [x.cleanup(self) for x in reversed(self._apps.values())]

    @staticmethod
    def create(sanic):

        am = ApplicationManager(sanic)
        for app_cfg in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(app_cfg)
        return am
