from sanic import Sanic

from os_sanic.cmdline import execute


class Manager(object):
    def __init__(self, app):
        self.app = app if app is not None else Sanic('os-sanic')

    def run(self, **kwargs):
        kwargs['app'] = self.app
        command_packages = kwargs.get('command_packages', [])
        if 'os_sanic.commands.project' not in command_packages:
            command_packages.insert(0, 'os_sanic.commands.project')
        kwargs['command_packages'] = command_packages
        execute(**kwargs)
