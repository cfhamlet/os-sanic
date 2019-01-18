from sanic.views import HTTPMethodView
from sanic.response import json
from os_config import Config


class Case01View(HTTPMethodView):

    def get(self, request):
        ext = self.application.get_extension('case01')
        return json({'view': ext.test()})


class Case02View(HTTPMethodView):

    def get(self, request):
        return json(Config.to_dict(self.config))
