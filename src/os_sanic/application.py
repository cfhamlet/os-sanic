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
        self.sanic = sanic
        self.name = name
        self.app_cfg = app_cfg
        self.core_config = core_config
        self.user_config = user_config

        self._logger = getLogger('App.{}'.format(name))

        self.extension_manager = ExtensionManager.create(self)

        self.view_manager = ViewManager.create(self)

        [setattr(self, m, partial(self.__call, m))
         for m in ('run', 'setup', 'cleanup')]

    @property
    def package(self):
        return self.app_cfg.package

    async def __call(self, method):
        try:
            await getattr(self.extension_manager, method)()
        except Exception as e:
            self._logger.error(
                'Method error {}, {}'.format(method, e))

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
        self.sanic = sanic
        self._apps = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)
        self._root_app = None

        [setattr(self, m, partial(self.__call, m))
         for m in ('run', 'setup', 'cleanup')]

    async def __call(self, method):
        iter = self._apps.keys()
        if method == 'cleanup':
            iter = sorted(iter, reverse=True)

        for key in iter:
            app = self._apps[key]
            try:
                await getattr(app, method)()

            except Exception as e:
                self._logger.error(
                    'Application error {}.{}, {}'.format(key, method, e))

    def get_app(self, name):
        return self._apps[name]

    @property
    def apps(self):
        return self._apps.values()

    def load_app(self, app_cfg):
        try:
            if isinstance(app_cfg, str):
                app_cfg = Config.create(package=app_cfg)
            if not Config.get(app_cfg, 'package'):
                self._logger.warn(
                    'Load app skip, no package {}'.format(app_cfg))
                return

            if Config.get(app_cfg, 'root') and self._root_app:
                self._logger.warn(
                    'Root app exist: {}'.format(self._root_app.name))
                Config.pop(app_cfg, 'root')

            app_name = app_cfg.package.split('.')[-1]
            app_name = Config.get(app_cfg, 'name', app_name)
            if app_name in self._apps:
                self._logger.warn('App already exists, {}'.format(app_name))
                return

            self._logger.debug(
                'Load app, {} {}'.format(app_name, app_cfg.package))
            app = Application.create(self.sanic, app_name, app_cfg)
            if Config.get(app_cfg, 'root'):
                self._root_app = app
            self._apps[app_name] = app
        except Exception as e:
            self._logger.error('Load app fail, {}, {}'.format(e, app_cfg))

    @classmethod
    def create(cls, sanic):

        am = cls(sanic)
        for app_cfg in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(app_cfg)
        return am
