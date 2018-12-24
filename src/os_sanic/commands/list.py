from os_sanic.commands import Command, CommandScope


class ListCommand(Command):
    name = 'list'
    scope = CommandScope.PROJECT
    help = 'list installed applications'
