import inspect

from sanic import Sanic

from os_sanic.cmdline import execute


def run(app=None, command_packages=None, **kwargs):
    if app is None:
        app = Sanic('os-sanic')

    if command_packages is None:
        command_packages = ['os_sanic.commands.project', ]

    execute(app=app, command_packages=command_packages, **kwargs)


def main():
    command_packages = ['os_sanic.commands.global', ]
    run(command_packages=command_packages)
