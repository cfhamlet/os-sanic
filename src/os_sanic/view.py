import os
from collections import OrderedDict

from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class, normalize_slash


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
        view_cls.config = config

        blueprint.add_route(view_cls.as_view(), uri)

        return cls(uri, view_cls, config)


class ViewManager(object):

    def __init__(self, application):
        self.application = application
        self.logger = application.get_logger(self.__class__.__name__)
        self.blueprint = self._create_blueprint()
        self._views = OrderedDict()
        self._load_views()
        self._load_statics()
        self.application.sanic.blueprint(self.blueprint)

    def _create_blueprint(self):
        _prefix = Config.get(self.application.app_cfg, 'prefix',
                             f'/{self.application.name}')
        prefix = normalize_slash(_prefix)

        if not prefix == _prefix:
            self.logger.warn(
                f'Normalize prefix from \'{_prefix}\' to \'{prefix}\'')

        return Blueprint(self.application.name, url_prefix=prefix)

    @property
    def views(self):
        return self._views.values()

    @property
    def statics(self):
        return self.blueprint.statics

    def _load_static(self, static_cfg, user_config):
        try:
            s = Config.to_dict(static_cfg)
            s.update(Config.to_dict(user_config))
            uri = s.pop('uri')

            real_uri = self._real_uri(uri)

            self.blueprint.static(real_uri, os.path.abspath(os.path.join(
                self.application.runtime_path, s.pop('file_or_directory'))), **s)
            static = self.statics[-1]
            pth = self.blueprint.url_prefix + static.uri
            self.logger.debug(
                f'Load static, {pth} {self.statics[-1]}')
        except Exception as e:
            self.logger.error(f'Load static error, {e}')

    def _real_uri(self, uri):
        real_uri = normalize_slash(uri, with_prefix_slash=False)
        url_prefix = self.blueprint.url_prefix

        warn = True if uri != real_uri else False
        if not url_prefix.endswith('/') and not real_uri.startswith('/'):
            warn = True
        elif url_prefix.endswith('/') and real_uri.startswith('/'):
            warn = True
            real_uri = real_uri[1:]
        if warn:
            self.logger.warn(
                f'Maybe misspell with prefix: \'{url_prefix}\' uri: \'{uri}\'')
        return real_uri

    def _load_view(self, view_cfg, user_configs):
        if isinstance(view_cfg, tuple):
            view_cfg = Config.create(uri=view_cfg[0], view_class=view_cfg[1])

        uri, view_class = view_cfg.uri, view_cfg.view_class
        user_config = user_configs.get(uri, Config.create())

        real_uri = self._real_uri(uri)
        view_cfg.uri = real_uri

        pth = self.blueprint.url_prefix+real_uri
        if real_uri in self._views:
            self.logger.warn(
                f'Skip, view already existed, {pth} {view_class}')
            return

        view = View.create(self.application, self.blueprint,
                           view_cfg, user_config)
        self._views[real_uri] = view
        self.logger.debug(f'Load view, {pth} {view.view_cls}')

    def _load_views(self):

        user_configs = {}
        for v in Config.get(self.application.user_config, 'VIEWS', []):
            if not isinstance(v, Config):
                continue
            uri = Config.pop(v, 'uri')
            if uri:
                user_configs[uri] = v
        for view_cfg in Config.get(self.application.core_config, 'VIEWS', []):
            try:
                self._load_view(view_cfg, user_configs)
            except Exception as e:
                self.logger.error(f'Load view error, {e}')

    def _load_statics(self):
        static_configs = dict([(cfg.uri, cfg) for cfg in Config.get(
            self.application.user_config, 'STATICS', [])])

        for static_cfg in Config.get(self.application.core_config, 'STATICS', []):
            self._load_static(static_cfg, static_configs.get(
                static_cfg.uri, Config.create()))
