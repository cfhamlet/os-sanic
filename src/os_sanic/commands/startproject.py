from os_sanic.commands import Command


class StartProjectCommand(Command):
    name = 'startproject'
    help='create new project'
