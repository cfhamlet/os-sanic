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


class Context(dict):
    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as ke:
            raise AttributeError(f"No '{ke.args[0]}'")


class Application(Workflowable):

    def __init__(self, name, context):
        self.name = name
        self.context = context
        self.logger = getLogger(f'App.{self.name}')
        self.extension_manager = ExtensionManager(self)
        self.view_manager = ViewManager(self)

        [setattr(self, method, partial(self.__call, method))
         for method in ('run', 'setup', 'cleanup')]

    @property
    def sanic(self):
        return self.application_manager.sanic

    def get_extension(self, extension_path):
        if '.' not in extension_path:
            extension_path = '.'.join((self.name, extension_path))

        return self.application_manager.get_extension(extension_path)

    def __getattr__(self, attr):
        try:
            if attr in self.context:
                return self.context[attr]
            return self[attr]
        except KeyError as ke:
            raise AttributeError("No '{}'".format(ke.args[0]))

    def get_logger(self, tag):
        return getLogger(f'App.{self.name}.{tag}')

    async def __call(self, method):
        try:
            await getattr(self.extension_manager, method)()
        except Exception as e:
            self.logger.error(f'Method error {method}, {e}')

    @staticmethod
    def create(application_manager, app_name, app_cfg):

        app_module = import_module('.'.join((app_cfg.package, 'app')))
        runtime_path = os.path.dirname(app_module.__file__)

        core_config = Config.from_object(app_module)
        user_config = Config.create()
        if Config.get(app_cfg, 'config'):
            f = os.path.join(os.getcwd(), app_cfg.config)
            user_config = Config.from_pyfile(f)
            runtime_path = os.path.dirname(f)

        context = Context()
        context.application_manager = application_manager
        context.runtime_path = runtime_path
        context.app_cfg = app_cfg
        context.core_config = core_config
        context.user_config = user_config

        return Application(app_name, context)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self.sanic = sanic
        self.logger = getLogger(self.__class__.__name__)
        self._apps = OrderedDict()
        self._load_apps()
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

    def get_app(self, name):
        return self._apps[name]

    def get_extension(self, extension_path):
        app_name, extension_name = extension_path.split('.')
        app = self.get_app(app_name)
        return app.extension_manager.get_extension(extension_name)

    @property
    def apps(self):
        return self._apps.values()

    def _load_apps(self):
        for app_cfg in Config.create(
                apps=self.sanic.config.get('INSTALLED_APPS', [])).apps:
            try:
                self._load_app(app_cfg)
            except Exception as e:
                self.logger.error(f'Load app fail, {e}, {app_cfg}')

    def _load_app(self, app_cfg):
        if isinstance(app_cfg, str):
            app_cfg = Config.create(package=app_cfg)
        if not Config.get(app_cfg, 'package'):
            self.logger.warn(f'Skip, no package {app_cfg}')
            return

        app_name = app_cfg.package.split('.')[-1]
        app_name = Config.get(app_cfg, 'name', app_name)
        if not app_name:
            self.logger.warn(f'Skip, no valid app name {app_cfg}')
            return
        if app_name in self._apps:
            self.logger.warn(f'Skip, app already exists, {app_name}')
            return

        self.logger.debug(
            f'Load app, {app_name} <package \'{app_cfg.package}>\'')
        app = Application.create(self, app_name, app_cfg)
        self._apps[app.name] = app
