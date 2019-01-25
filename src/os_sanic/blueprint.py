import inspect
import os

from sanic import Blueprint
from sanic.views import CompositionView, HTTPMethodView

from os_sanic.prototype import AppCfg, RouteCfg, StaticCfg, URIModel
from os_sanic.utils import load_obj, normalize_slash


def adapt_uri(url_prefix, uri):
    real_uri = normalize_slash(uri, with_prefix_slash=False)

    if url_prefix.endswith('/') and real_uri.startswith('/'):
        real_uri = real_uri[1:]

    return real_uri


def new_blueprint(application):
    app_cfg = application.app_cfg
    prefix = app_cfg.url_prefix

    if not prefix:
        prefix = f'/{app_cfg.name}'

    url_prefix = normalize_slash(prefix)

    if not prefix == url_prefix:
        application.logger.warn(
            f"Normalize prefix from '{prefix}' to '{url_prefix}'")

    include = set(AppCfg.__fields__.keys()) - set(['package', 'config'])
    return Blueprint(**app_cfg.copy(update={'url_prefix': url_prefix}).dict(include=include))


def load_route(application, blueprint, route_cfg, user_cfg):
    config = route_cfg.copy(update=user_cfg.copy(
        exclude=set(['handler'])).dict())

    package = None
    if config.handler.startswith('.'):
        package = application.app_cfg.package

    real_uri = adapt_uri(blueprint.url_prefix, config.uri)

    include = inspect.getfullargspec(blueprint.add_route).args[3:]
    handler = load_obj(config.handler, package=package)
    if inspect.isclass(handler) and issubclass(handler, (HTTPMethodView, CompositionView)):
        if issubclass(handler, HTTPMethodView):
            handler.application = application
            handler.config = config

        blueprint.add_route(handler.as_view(), real_uri,
                            config.dict(include=include))
    elif inspect.isfunction(handler):
        for method in config.methods:
            call = getattr(blueprint, method.lower())
            include = inspect.getfullargspec(call).args[2:]
            call(real_uri, **config.dict(include=include))(handler)
    else:
        raise ValueError(f'Not supported type: {type(handler)}')

    pth = blueprint.url_prefix+real_uri
    application.logger.debug(f'Load route, {pth} {handler}')


def load_routes(application, blueprint):
    user_cfgs = dict([(cfg['uri'], URIModel(**cfg))
                      for cfg in application.user_cfg.ROUTES if 'uri' in cfg])

    for cfg in application.core_cfg.ROUTES:
        try:
            route_cfg = RouteCfg(**dict(zip(RouteCfg.__fields__.keys(), cfg))) \
                if isinstance(cfg, tuple) \
                else RouteCfg(**cfg)

            load_route(application, blueprint, route_cfg,
                       user_cfgs.get(route_cfg.uri, route_cfg))
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
            load_static(application, blueprint, static_cfg,
                        user_cfgs.get(static_cfg.uri, static_cfg))
        except Exception as e:
            application.logger.error(f'Load static error, {e}, {cfg}')


def load_middlewares(application, blueprint):
    for mid in application.core_cfg.MIDDLEWARES:
        try:
            package = None
            if mid.startswith('.'):
                package = application.app_cfg.package

            middleware = load_obj(mid, package=package)

            attach_to = {1: 'request', 2: 'response'}.get(
                len(inspect.getfullargspec(middleware).args))

            blueprint.middleware(attach_to=attach_to)(middleware)

            application.logger.debug(f'Load middleware {middleware}')

        except Exception as e:
            application.logger.error(f'Load middleware error, {e}, {mid}')


def load_exception_handlers(application, blueprint):
    for cfg in application.core_cfg.EXCEPTIONS:
        try:
            handler, exceptions = cfg
            if isinstance(exceptions, str):
                exceptions = [exceptions]

            package = None
            if handler.startswith('.'):
                package = application.app_cfg.package

            handler = load_obj(handler, package=package)
            exceptions = [load_obj(e) for e in exceptions]

            blueprint.exception(*exceptions)(handler)

            application.logger.debug(
                f'Load exception handler {handler}, {exceptions}')

        except Exception as e:
            application.logger.error(
                f'Load exception handler error, {e}, {cfg}')


def create(application):
    blueprint = new_blueprint(application)
    for loader in [load_routes,
                   load_middlewares,
                   load_exception_handlers,
                   load_statics]:
        loader(application, blueprint)
    application.sanic.blueprint(blueprint)
    return blueprint
