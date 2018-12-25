from os_config import Config
from sanic import Blueprint
from sanic.views import HTTPMethodView

from os_sanic.utils import load_class


class ViewManager(object):
    @staticmethod
    def load(sanic, app_cfg, core, config):

        bp = Blueprint(app_cfg.name)

        configs = {}
        for v in config.get('VIEWS', []):
            pattern = v.get('pattern')
            if pattern:
                configs[pattern] = v

        for cfg in core.get('VIEWS', []):
            pattern = cfg.get('pattern')
            if pattern:
                c = Config.create()
                c.update(cfg)
                if pattern in configs is not None:
                    c.update(configs.get(pattern))
                c.view_class = cfg.view_class
                view_cls = load_class(cfg.view_class, HTTPMethodView)
                bp.add_route(view_cls().as_view(view_config=c), pattern)
        sanic.blueprint(bp)
