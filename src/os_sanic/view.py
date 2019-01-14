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

    def _load_view(self, view_cfg, user_config):

        if isinstance(view_cfg, tuple):
            view_cfg = Config.create(uri=view_cfg[0], view_class=view_cfg[1])

        uri, view_class = view_cfg.uri, view_cfg.view_class

        if uri in self._views:
            self.logger.warn(f'View already existed, {uri} {view_class}')
            return

        view = View.create(self.application, self.blueprint,
                           view_cfg, user_config)
        self._views[uri] = view
        pth = self.blueprint.url_prefix+uri if self.blueprint.url_prefix else uri
        self.logger.debug(f'Load view, {pth} {view.view_cls}')

    def load_view(self, view_cfg, user_config):
        try:
            self._load_view(view_cfg, user_config)
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

        configs = {}
        for v in Config.get(application.user_config, 'VIEWS', []):
            uri = Config.get(v, 'uri')
            if uri:
                Config.pop(v, 'uri')
                configs[uri] = v

        for view_cfg in Config.get(application.core_config, 'VIEWS', []):
            view_manager.load_view(view_cfg, configs.get(
                view_cfg.uri, Config.create()))

        application.sanic.blueprint(blueprint)

        return view_manager
