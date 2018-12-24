from os_sanic.commands import Command, CommandScope


class RunCommand(Command):
    name = 'run'
    scope = CommandScope.PROJECT
    help = 'run server'
