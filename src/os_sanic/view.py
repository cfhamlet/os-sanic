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

    @staticmethod
    def create(application, blueprint, view_cfg, user_config):

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

        if len(config) > 0:
            blueprint.add_route(view_cls.as_view(
                config=config), pattern)
        else:
            blueprint.add_route(view_cls.as_view(), pattern)

        return View(pattern, view_cls, config)


class ViewManager(object):

    def __init__(self, application):
        self.application = application
        self._views = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)

        prefix = None
        if not Config.get(application.app_cfg, 'root'):
            prefix = Config.get(application.app_cfg,
                                'prefix', '/' + application.name)
        self.blueprint = Blueprint(application.name, url_prefix=prefix)
        self.application.sanic.blueprint(self.blueprint)

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
            self._logger.warn(
                'View already existed, {} {}'.format(pattern, view_class))
            return

        view = View.create(
            self.application, self.blueprint, view_cfg, configs.get(pattern, Config.create()))
        self._views[pattern] = view
        self._logger.debug('Load view, {} {}'.format(
            self.blueprint.url_prefix+pattern if self.blueprint.url_prefix else pattern, view.view_cls))

    def load_view(self, view_cfg, configs):
        try:
            self._load_view(view_cfg, configs)
        except Exception as e:
            self._logger.error('Load view error, {}'.format(e))

    @staticmethod
    def create(application):
        view_manager = ViewManager(application)

        configs = {}
        for v in Config.get(application.user_config, 'VIEWS', []):
            pattern = Config.get(v, 'pattern')
            if pattern:
                Config.pop(v, 'pattern')
                configs[pattern] = v

        for view_cfg in Config.get(application.core_config, 'VIEWS', []):
            view_manager.load_view(view_cfg, configs)

        return view_manager
