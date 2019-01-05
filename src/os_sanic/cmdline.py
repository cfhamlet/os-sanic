import click

from os_sanic.utils import walk_modules


class CommandFinder(click.MultiCommand):
    def list_commands(self, ctx):
        return list(self.__find_commnds(ctx.obj).keys())

    def __find_commnds(self, path):
        commands = {}
        for cmd_module in walk_modules(path, skip_fail=False):
            if hasattr(cmd_module, 'cli'):
                commands[cmd_module.__name__.split(
                    '.')[-1]] = cmd_module.cli

        return commands

    def get_command(self, ctx, name):
        commands = self.__find_commnds(ctx.obj)
        return commands[name]


def execute(scope='global'):

    @click.command(cls=CommandFinder, context_settings=dict(obj=f'os_sanic.commands.{scope}'))
    @click.version_option(message='%(prog)s %(version)s')
    @click.pass_context
    def cli(ctx):
        '''Command line tool for os-sanic.'''
        pass

    cli()
