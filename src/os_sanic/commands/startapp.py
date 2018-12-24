from os_sanic.commands import Command, CommandScope


class StartAppCommand(Command):
    name = 'startapp'
    scope = CommandScope.PROJECT
    help = 'create new application'
