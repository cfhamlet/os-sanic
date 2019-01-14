import os
import inspect
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

    def __init__(self, sanic, app_cfg, core_config, user_config):
        self.sanic = sanic
        self.app_cfg = app_cfg
        self.core_config = core_config
        self.user_config = user_config

        self.logger = getLogger(f'App.{app_cfg.name}')

        self.extension_manager = ExtensionManager.create(self)

        self.view_manager = ViewManager.create(self)

        [setattr(self, method, partial(self.__call, method))
         for method in ('run', 'setup', 'cleanup')]

    @property
    def name(self):
        return self.app_cfg.name

    def get_logger(self, tag):
        return getLogger(f'App.{self.name}.{tag}')

    @property
    def package(self):
        return self.app_cfg.package

    async def __call(self, method):
        try:
            await getattr(self.extension_manager, method)()
        except Exception as e:
            self.logger.error(f'Method error {method}, {e}')

    @staticmethod
    def create(sanic, app_cfg):

        app_module = import_module('.'.join((app_cfg.package, 'app')))
        core_config = Config.from_object(app_module)
        user_config = Config.create()
        if Config.get(app_cfg, 'config'):
            f = os.path.join(os.getcwd(), app_cfg.config)
            user_config = Config.from_pyfile(f)

        return Application(sanic, app_cfg, core_config, user_config)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self.sanic = sanic
        self.logger = getLogger(self.__class__.__name__)
        self._apps = OrderedDict()
        self._root_app = None
        [setattr(self, method, partial(self.__call, method))
         for method in ('run', 'setup', 'cleanup')]

    async def __call(self, method):
        iter = self._apps.keys()
        if method == 'cleanup':
            iter = sorted(iter, reverse=True)

        for key in iter:
            app = self._apps[key]
            try:
                await getattr(app, method)()
            except Exception as e:
                self.logger.error(f'Application error {key}.{method}, {e}')

    def get_extension(self, extension_path):
        app_name, extension_name = extension_path.split('.')
        app = self.get_app(app_name)
        return app.extension_manager.get_extension(extension_name)

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
                self.logger.warn(f'Load app skip, no package {app_cfg}')
                return

            if Config.get(app_cfg, 'root') and self._root_app:
                self.logger.warn(f'Root app exist: {self._root_app.name}')
                Config.pop(app_cfg, 'root')

            app_name = app_cfg.package.split('.')[-1]
            app_name = Config.get(app_cfg, 'name', app_name)
            app_cfg.name = app_name
            if app_name in self._apps:
                self.logger.warn(f'App already exists, {app_name}')
                return

            self.logger.debug(
                f'Load app, {app_name} <package \'{app_cfg.package}>\'')
            app = Application.create(self.sanic, app_cfg)
            if Config.get(app_cfg, 'root'):
                self._root_app = app
            self._apps[app_name] = app
        except Exception as e:
            self.logger.error(f'Load app fail, {e}, {app_cfg}')

    @classmethod
    def create(cls, sanic):

        assert not hasattr(
            sanic, 'application'), 'sanic instance already has \'application\' attribute'

        am = cls(sanic)
        for app_cfg in Config.create(
                apps=sanic.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(app_cfg)
        sanic.application = am
        return am
