import os
from collections import OrderedDict
from functools import partial
from importlib import import_module
from inspect import isawaitable

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
        self._logger = getLogger('App.{}'.format(name))
        self._ext_manager = ExtensionManager.create(
            sanic, app_cfg, core_config, user_config)
        ViewManager.load(sanic, name, app_cfg, core_config, user_config)
        [setattr(self, m, partial(self.__call, m))
         for m in ('run', 'setup', 'cleanup')]

    async def __call(self, method):
        try:
            await getattr(self._ext_manager, method)()
        except Exception as e:
            self._logger.error(
                'App error {}.{}, {}'.format(self.name, method, e))

    @staticmethod
    def create(sanic, app_name, app_cfg):

        app_module = import_module('.'.join((app_cfg.package, 'app')))
        core_config = Config.from_object(app_module)
        user_config = Config.create()
        if Config.get(app_cfg, 'config'):
            f = os.path.join(os.getcwd(), app_cfg.config)
            user_config = Config.from_pyfile(f)

        return Application(sanic, app_name, app_cfg, core_config, user_config)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self._sanic = sanic
        self._apps = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)

    def load_app(self, app_cfg):
        try:
            if isinstance(app_cfg, str):
                app_cfg = Config.create(package=app_cfg)
            if not Config.get(app_cfg, 'package'):
                self._logger.warn(
                    'Load app skip, no package {}'.format(app_cfg))
                return

            app_name = app_cfg.package.split('.')[-1]
            app_name = Config.get(app_cfg, 'name', app_name)
            if app_name in self._apps:
                self._logger.warn('App already exists, {}'.format(app_name))
                return

            self._logger.debug(
                'Load app, {} {}'.format(app_name, app_cfg.package))
            app = Application.create(self._sanic, app_name, app_cfg)
            self._apps[app_name] = app
        except Exception as e:
            self._logger.error('Load app fail, {}, {}'.format(e, app_cfg))

    async def run(self):
        for app in self._apps.values():
            await app.run()

    async def setup(self):
        for app in self._apps.values():
            await app.setup()

    async def cleanup(self):
        for app in reversed(self._apps.values()):
            await app.cleanup()

    @staticmethod
    def create(sanic):

        am = ApplicationManager(sanic)
        for app_cfg in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(app_cfg)
        return am
