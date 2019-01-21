import os
from collections import OrderedDict

from pydantic import BaseModel
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class, normalize_slash


class URIModel(BaseModel):
    uri: str

    class Config:
        allow_extra = True


class ViewCfg(URIModel):
    view_class: str


class StaticCfg(URIModel):
    file_or_directory: str


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
        _prefix = self.application.app_cfg.prefix

        if not _prefix:
            _prefix = f'/{self.application.name}'

        prefix = normalize_slash(_prefix)

        if not prefix == _prefix:
            self.logger.warn(
                f'Normalize prefix from \'{_prefix}\' to \'{prefix}\'')

        return Blueprint(self.application.name, url_prefix=prefix)

    @property
    def views(self):
        return self._views.items()

    @property
    def statics(self):
        return self.blueprint.statics

    def _load_static(self, static_cfg, user_cfg):
        try:
            config = static_cfg.copy(update=user_cfg.dict())
            real_uri = self._real_uri(config.uri)

            self.blueprint.static(real_uri, os.path.abspath(os.path.join(
                self.application.runtime_path, config.file_or_directory)),
                **config.dict(exclude=set(['uri', 'file_or_directory'])))

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

    def _load_view(self, view_cfg, user_cfg):
        config = view_cfg.copy(update=user_cfg.copy(
            exclude=set(['view_class'])).dict())

        real_uri = self._real_uri(config.uri)

        pth = self.blueprint.url_prefix+real_uri
        if real_uri in self._views:
            self.logger.warn(
                f'Skip, view already existed, {pth} {view_cfg.view_class}')
            return

        package = None
        if config.view_class.startswith('.'):
            package = self.application.app_cfg.package
        view_cls = load_class(
            config.view_class, HTTPMethodView, package=package)

        view_cls.application = self.application
        view_cls.config = config

        view = self.blueprint.add_route(view_cls.as_view(), real_uri)

        self._views[real_uri] = view
        self.logger.debug(f'Load view, {pth} {view.view_class}')

    def _load_views(self):

        user_cfgs = dict([(cfg['uri'], URIModel(**cfg))
                          for cfg in self.application.user_cfg.VIEWS if 'uri' in cfg])

        for cfg in self.application.core_cfg.VIEWS:
            try:
                if isinstance(cfg, tuple):
                    cfg = dict(uri=cfg[0], view_class=cfg[1])
                view_cfg = ViewCfg(**cfg)

                self._load_view(view_cfg, user_cfgs.get(
                    view_cfg.uri, view_cfg))
            except Exception as e:
                self.logger.error(f'Load view error, {e}')

    def _load_statics(self):
        user_cfgs = dict([(cfg['uri'], URIModel(**cfg))
                          for cfg in self.application.user_cfg.STATICS if 'uri' in cfg])

        for cfg in self.application.core_cfg.STATICS:
            static_cfg = StaticCfg(**cfg)
            self._load_static(static_cfg, user_cfgs.get(
                static_cfg.uri, static_cfg))
