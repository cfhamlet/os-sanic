from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.log import getLogger
from os_sanic.utils import load_class


class ViewManager(object):

    @staticmethod
    def load_view(bp, app_cfg, view_cfg, configs):

        pattern = None
        view_cls = None
        if isinstance(view_cfg, tuple):
            pattern, view_class = view_cfg
        else:
            pattern, view_class = view_cfg.pattern, view_cfg.view_class

        view_config = Config.create()
        view_config.update(view_cfg)
        if pattern in configs:
            view_config.update(configs.get(pattern))
        view_config.pop('pattern')
        view_config.pop('view_class')

        package = None
        if view_class.startswith('.'):
            package = app_cfg.package
        view_cls = load_class(
            view_class, HTTPMethodView, package=package)

        if len(view_config) > 0:
            bp.add_route(view_cls.as_view(
                view_config=view_config), pattern)
        else:
            bp.add_route(view_cls.as_view(), pattern)

        return pattern, view_cls

    @staticmethod
    def load(sanic, app_name, app_cfg, core_config, user_config):
        logger = getLogger('ViewManager')

        prefix = None
        if not app_cfg.get('root'):
            prefix = app_cfg.get('prefix', '/' + app_name)
        bp = Blueprint(app_name, url_prefix=prefix)

        configs = {}
        for v in user_config.get('VIEWS', []):
            pattern = v.get('pattern')
            if pattern:
                v.pop('pattern')
                configs[pattern] = v

        logger = getLogger('ViewManager')
        for view_cfg in core_config.get('VIEWS', []):
            try:
                pattern, view_cls = ViewManager.load_view(
                    bp, app_cfg, view_cfg, configs)
                logger.debug('Load view, {} {}'.format(
                    pattern if not prefix else prefix+pattern, view_cls))
            except Exception as e:
                logger.error('Load view error, {}'.format(e))

        sanic.blueprint(bp)
