import inspect
import os
from collections import OrderedDict
from functools import partial
from importlib import import_module
from inspect import isawaitable
from typing import List

from pydantic import BaseModel

from os_sanic.extension import ExtensionCfg, ExtensionManager
from os_sanic.log import getLogger
from os_sanic.utils import NamedModel, load_module_from_pyfile
from os_sanic.workflow import Workflowable
from os_sanic import blueprint


class AppCfg(NamedModel):
    package: str
    prefix: str = None
    config: str = None


class ApplicationCfg(BaseModel):
    EXTENSIONS: List = []
    VIEWS: List = []
    STATICS: List = []

    class Config:
        ignore_extra = True


class Context(BaseModel):
    app_cfg: AppCfg
    core_cfg: ApplicationCfg
    user_cfg: ApplicationCfg
    runtime_path: str


class Application(Workflowable):

    def __init__(self, application_manager, context):
        self.context = context
        self.application_manager = application_manager

        [setattr(self, method, partial(self.__call, method))
         for method in ('setup', 'cleanup')]

        [setattr(self, field, getattr(context, field))
         for field in context.fields.keys()]

        self.logger = getLogger(f'App.{self.name}')

        self.extension_manager = ExtensionManager(self)
        self.blueprint = blueprint.create(self)

    @property
    def name(self):
        return self.app_cfg.name

    @property
    def sanic(self):
        return self.application_manager.sanic

    def get_extension(self, extension_path):
        if '.' not in extension_path:
            extension_path = '.'.join((self.name, extension_path))

        return self.application_manager.get_extension(extension_path)

    def get_logger(self, tag):
        return getLogger(f'App.{self.name}.{tag}')

    async def __call(self, method):
        try:
            await getattr(self.extension_manager, method)()
        except Exception as e:
            self.logger.error(f'Method error {method}, {e}')

    @staticmethod
    def create(application_manager, app_cfg):

        app_module = import_module('.'.join((app_cfg.package, 'app')))
        runtime_path = os.path.dirname(app_module.__file__)
        core_cfg = ApplicationCfg.parse_obj(app_module.__dict__)

        user_cfg = ApplicationCfg()
        if app_cfg.config:
            f = os.path.join(os.getcwd(), app_cfg.config)
            user_cfg = ApplicationCfg.parse_obj(
                load_module_from_pyfile(f).__dict__)
            runtime_path = os.path.dirname(f)

        context = Context(
            app_cfg=app_cfg,
            core_cfg=core_cfg,
            user_cfg=user_cfg,
            runtime_path=runtime_path,
        )

        return Application(application_manager, context)


class ApplicationManager(Workflowable):

    def __init__(self, sanic):
        self.sanic = sanic
        self.logger = getLogger(self.__class__.__name__)
        self._apps = OrderedDict()
        self._load_apps()
        [setattr(self, method, partial(self.__call, method))
         for method in ('setup', 'cleanup')]

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
        for cfg in self.sanic.config.get('INSTALLED_APPS', []):
            try:
                self._load_app(cfg)
            except Exception as e:
                self.logger.error(f'Load app fail, {e}, {cfg}')

    def _load_app(self, cfg):

        if isinstance(cfg, str):
            cfg = dict(package=cfg)

        cfg.setdefault('name', cfg['package'].split('.')[-1])
        name = cfg['name']
        if name in self._apps:
            self.logger.warn(f'Skip, app already exists, {name}')
            return

        app_cfg = AppCfg(**cfg)
        self.logger.debug(
            f'Load app, {name} <package \'{app_cfg.package}>\'')

        app = Application.create(self, app_cfg)
        self._apps[name] = app
