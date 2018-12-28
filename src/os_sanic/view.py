from collections import OrderedDict

from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.log import getLogger
from os_sanic.utils import load_class


class View(object):
    def __init__(self, blueprint, pattern, view_cls, config):
        self._pattern = pattern
        self._blueprint = blueprint
        self._view_cls = view_cls
        self._config = config

    @classmethod
    def create(cls, blueprint, pattern, view_class, view_cfg, configs):
        view_config = Config.create()
        Config.update(view_config, view_cfg)
        if pattern in configs:
            Config.update(view_config, configs.get(pattern))
        Config.pop(view_config, 'pattern')
        Config.pop(view_config, 'view_class')

        package = None
        if view_class.startswith('.'):
            package = self._app_cfg.package
        view_cls = load_class(
            view_class, HTTPMethodView, package=package)

        if len(view_config) > 0:
            self._blueprint.add_route(view_cls.as_view(
                view_config=view_config), pattern)
        else:
            self._blueprint.add_route(view_cls.as_view(), pattern)

        return View(blueprint, pattern, view_cls, config)


class ViewManager(object):

    def __init__(self, sanic, app_name, app_cfg):
        self._sanic = sanic
        self._app_name = app_name
        self._app_cfg = app_cfg
        self._views = OrderedDict()
        self._logger = getLogger(self.__class__.__name__)

        prefix = None
        if not Config.get(app_cfg, 'root'):
            prefix = Config.get(app_cfg, 'prefix', '/' + app_name)
        self._blueprint = Blueprint(app_name, url_prefix=prefix)
        self._sanic.blueprint(self._blueprint)

    @property
    def views(self):
        return self._views.values()

    @property
    def blueprint(self):
        return self._blueprint

    def _load_view(self, view_cfg, configs):

        pattern = None
        view_cls = None
        if isinstance(view_cfg, tuple):
            pattern, view_class = view_cfg
        else:
            pattern, view_class = view_cfg.pattern, view_cfg.view_class

        if pattern in self._views:
            self._logger.warn(
                'View already existed, {} {}'.format(pattern, view_class))
            return

        view_config = Config.create()
        Config.update(view_config, view_cfg)
        if pattern in configs:
            Config.update(view_config, configs.get(pattern))
        Config.pop(view_config, 'pattern')
        Config.pop(view_config, 'view_class')

        package = None
        if view_class.startswith('.'):
            package = self._app_cfg.package
        view_cls = load_class(
            view_class, HTTPMethodView, package=package)

        if len(view_config) > 0:
            self._blueprint.add_route(view_cls.as_view(
                view_config=view_config), pattern)
        else:
            self._blueprint.add_route(view_cls.as_view(), pattern)

        self._views[pattern] = View.create()
        self._logger.debug('Load view, {} {}'.format(
            self._blueprint.url_prefix+pattern if self._blueprint.url_prefix else pattern, view_cls))

    def load_view(self, view_cfg, configs):
        try:
            self._load_view(view_cfg, configs)
        except Exception as e:
            self._logger.error('Load view error, {}'.format(e))

    @staticmethod
    def load(sanic, app_name, app_cfg, core_config, user_config):
        view_manager = ViewManager(sanic, app_name, app_cfg)

        configs = {}
        for v in Config.get(user_config, 'VIEWS', []):
            pattern = Config.get(v, 'pattern')
            if pattern:
                Config.pop(v, 'pattern')
                configs[pattern] = v

        for view_cfg in Config.get(core_config, 'VIEWS', []):
            view_manager.load_view(view_cfg, configs)

        return view_manager
