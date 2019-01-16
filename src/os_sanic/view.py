import os
from collections import OrderedDict

from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class


class View(object):
    def __init__(self, uri, view_cls, config):
        self.uri = uri
        self.view_cls = view_cls
        self.config = config

    @classmethod
    def create(cls, application, blueprint, view_cfg, user_config):

        uri, view_class = view_cfg.uri, view_cfg.view_class
        config = Config.create()
        Config.update(config, view_cfg)
        Config.update(config, user_config)
        Config.pop(config, 'uri')
        Config.pop(config, 'view_class')

        package = None
        if view_class.startswith('.'):
            package = application.app_cfg.package
        view_cls = load_class(
            view_class, HTTPMethodView, package=package)

        view_cls.application = application

        kwargs = {}
        if len(config) > 0:
            kwargs['config'] = config

        blueprint.add_route(view_cls.as_view(**kwargs), uri)

        return cls(uri, view_cls, config)


class ViewManager(object):

    def __init__(self, application, blueprint):
        self.application = application
        self.blueprint = blueprint
        self._views = OrderedDict()
        self.logger = application.get_logger(self.__class__.__name__)

    @property
    def views(self):
        return self._views.values()

    @property
    def statics(self):
        return self.blueprint.statics

    def load_static(self, static_config, user_config):
        try:
            s = Config.to_dict(static_config)
            s.update(Config.to_dict(user_config))
            self.blueprint.static(s.pop('uri'), os.path.abspath(os.path.join(
                self.application.runtime_path, s.pop('file_or_directory'))), **s)
            static = self.statics[-1]
            pth = self.blueprint.url_prefix + \
                static.uri if self.blueprint.url_prefix else static.uri
            self.logger.debug(
                f'Load static, {pth} {self.statics[-1]}')
        except Exception as e:
            self.logger.error(f'Load static error, {e}')

    def _load_view(self, view_cfg, user_configs):
        if isinstance(view_cfg, tuple):
            view_cfg = Config.create(uri=view_cfg[0], view_class=view_cfg[1])

        uri, view_class = view_cfg.uri, view_cfg.view_class
        user_config = user_configs.get(uri, Config.create())

        pth = self.blueprint.url_prefix+uri if self.blueprint.url_prefix else uri
        if uri in self._views:
            self.logger.warn(
                f'View already existed, {pth} {view_class}')
            return

        view = View.create(self.application, self.blueprint,
                           view_cfg, user_config)
        self._views[uri] = view
        self.logger.debug(f'Load view, {pth} {view.view_cls}')

    def load_view(self, view_cfg, user_configs):
        try:
            self._load_view(view_cfg, user_configs)
        except Exception as e:
            self.logger.error(f'Load view error, {e}')

    @classmethod
    def create(cls, application):
        prefix = None
        if not Config.get(application.app_cfg, 'root'):
            prefix = Config.get(application.app_cfg,
                                'prefix', '/' + application.name)

        blueprint = Blueprint(application.name, url_prefix=prefix)

        view_manager = cls(application, blueprint)

        user_configs = {}
        for v in Config.get(application.user_config, 'VIEWS', []):
            if not isinstance(v, Config):
                continue
            uri = Config.get(v, 'uri')
            if uri:
                Config.pop(v, 'uri')
                user_configs[uri] = v

        for view_cfg in Config.get(application.core_config, 'VIEWS', []):
            view_manager.load_view(view_cfg, user_configs)

        static_configs = {}
        for v in Config.get(application.user_config, 'STATICS', []):
            uri = Config.get(v, 'uri')
            if uri:
                Config.pop(v, 'uri')
                static_configs[uri] = v
        statics_config = Config.get(application.core_config, 'STATICS', [])
        for static_config in statics_config:
            view_manager.load_static(static_config, static_configs.get(
                static_config.uri, Config.create()))

        application.sanic.blueprint(blueprint)

        return view_manager
