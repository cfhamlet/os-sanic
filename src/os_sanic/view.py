from collections import OrderedDict

from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.log import getLogger
from os_sanic.utils import load_class


class View(object):
    def __init__(self, pattern, view_cls, config):
        self.pattern = pattern
        self.view_cls = view_cls
        self.config = config

    @classmethod
    def create(cls, application, blueprint, view_cfg, user_config):

        pattern, view_class = view_cfg.pattern, view_cfg.view_class
        config = Config.create()
        Config.update(config, view_cfg)
        Config.update(config, user_config)
        Config.pop(config, 'pattern')
        Config.pop(config, 'view_class')

        package = None
        if view_class.startswith('.'):
            package = application.app_cfg.package
        view_cls = load_class(
            view_class, HTTPMethodView, package=package)

        kwargs = {}
        if len(config) > 0:
            kwargs['config'] = config

        blueprint.add_route(view_cls.as_view(**kwargs), pattern)

        return cls(pattern, view_cls, config)


class ViewManager(object):

    def __init__(self, application, blueprint):
        self.application = application
        self.blueprint = blueprint
        self._views = OrderedDict()
        self.logger = getLogger(self.__class__.__name__)

    @property
    def views(self):
        return self._views.values()

    def _load_view(self, view_cfg, configs):

        pattern = None
        if isinstance(view_cfg, tuple):
            pattern, view_class = view_cfg
            view_cfg = Config.create(
                pattern=view_cfg.pattern, view_class=view_cfg._view_class)

        pattern, view_class = view_cfg.pattern, view_cfg.view_class

        if pattern in self._views:
            self.logger.warn(f'View already existed, {pattern} {view_class}')
            return

        view = View.create(
            self.application, self.blueprint, view_cfg, configs.get(pattern, Config.create()))
        self._views[pattern] = view
        pth = self.blueprint.url_prefix+pattern if self.blueprint.url_prefix else pattern
        self.logger.debug(f'Load view, {pth} {view.view_cls}')

    def load_view(self, view_cfg, configs):
        try:
            self._load_view(view_cfg, configs)
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
            pattern = Config.get(v, 'pattern')
            if pattern:
                Config.pop(v, 'pattern')
                configs[pattern] = v

        for view_cfg in Config.get(application.core_config, 'VIEWS', []):
            view_manager.load_view(view_cfg, configs)

        application.sanic.blueprint(blueprint)

        return view_manager
