from sanic.views import HTTPMethodView
from sanic.response import json


class Case01View(HTTPMethodView):

    def get(self, request):
        ext = self.application.get_extension('case01')
        return json({'view': ext.test()})
