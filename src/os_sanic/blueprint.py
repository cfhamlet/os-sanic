import os

from pydantic import BaseModel
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class, normalize_slash


class URIModel(BaseModel):
    uri: str

    class Config:
        allow_extra = True


class RouteCfg(URIModel):
    view_class: str


class StaticCfg(URIModel):
    file_or_directory: str


def adapt_uri(url_prefix, uri):
    real_uri = normalize_slash(uri, with_prefix_slash=False)

    if url_prefix.endswith('/') and real_uri.startswith('/'):
        real_uri = real_uri[1:]

    return real_uri


def new_blueprint(application):
    _prefix = application.app_cfg.prefix

    if not _prefix:
        _prefix = f'/{application.name}'

    prefix = normalize_slash(_prefix)

    if not prefix == _prefix:
        application.logger.warn(
            f'Normalize prefix from \'{_prefix}\' to \'{prefix}\'')

    return Blueprint(application.name, url_prefix=prefix)


def load_route(application, blueprint, route_cfg, user_cfg):
    config = route_cfg.copy(update=user_cfg.copy(
        exclude=set(['view_class'])).dict())

    package = None
    if config.view_class.startswith('.'):
        package = application.app_cfg.package
    view_cls = load_class(
        config.view_class, HTTPMethodView, package=package)

    view_cls.application = application
    view_cls.config = config

    real_uri = adapt_uri(blueprint.url_prefix, config.uri)
    view = blueprint.add_route(view_cls.as_view(), real_uri)

    pth = blueprint.url_prefix+real_uri
    application.logger.debug(f'Load route, {pth} {view.view_class}')


def load_routes(application, blueprint):
    user_cfgs = dict([(cfg['uri'], URIModel(**cfg))
                      for cfg in application.user_cfg.ROUTES if 'uri' in cfg])

    for cfg in application.core_cfg.ROUTES:
        try:
            if isinstance(cfg, tuple):
                cfg = dict(uri=cfg[0], view_class=cfg[1])
            route_cfg = RouteCfg(**cfg)

            load_route(application, blueprint, route_cfg, user_cfgs.get(
                route_cfg.uri, route_cfg))
        except Exception as e:
            application.logger.error(f'Load route error, {e}, {cfg}')


def load_static(application, blueprint, static_cfg, user_cfg):
    config = static_cfg.copy(update=user_cfg.dict())
    real_uri = adapt_uri(blueprint.url_prefix, config.uri)

    blueprint.static(real_uri, os.path.abspath(os.path.join(
        application.runtime_path, config.file_or_directory)),
        **config.dict(exclude=set(['uri', 'file_or_directory'])))

    static = blueprint.statics[-1]
    pth = blueprint.url_prefix + static.uri
    application.logger.debug(
        f'Load static, {pth} {blueprint.statics[-1]}')


def load_statics(application, blueprint):
    user_cfgs = dict([(cfg['uri'], URIModel(**cfg))
                      for cfg in application.user_cfg.STATICS if 'uri' in cfg])

    for cfg in application.core_cfg.STATICS:
        try:
            static_cfg = StaticCfg(**cfg)
            load_static(application, blueprint, static_cfg, user_cfgs.get(
                static_cfg.uri, static_cfg))
        except Exception as e:
            application.logger.error(f'Load static error, {e}, {cfg}')


def create(application):
    blueprint = new_blueprint(application)
    load_routes(application, blueprint)
    load_statics(application, blueprint)
    application.sanic.blueprint(blueprint)
    return blueprint
