from importlib import import_module

from os_config import Config


class Application(object):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def create(app_config):
        print(app_config)
        package = app_config['package']
        name = package.split('.')[-1]
        name = app_config.get('namespace', name)
        config_module = import_module('.'.join((package, 'config')))

        return Application(name)


class ApplicationManager(object):

    def __init__(self, sanic_app):
        self._sanic = sanic_app
        self._apps = {}

    def load_app(self, app_config):
        app = Application.create(app_config)
        self._apps[app.name] = app

    @staticmethod
    def create(sanic_app):

        am = ApplicationManager(sanic_app)
        for app_config in Config.create(
                apps=sanic_app.config.get('INSTALLED_APPS', [])).apps:
            am.load_app(app_config)
        return am
