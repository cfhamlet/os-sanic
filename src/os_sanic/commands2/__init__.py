import click
import ast
from os_sanic.utils import walk_modules
from importlib import import_module
from logging import _nameToLevel


def valid_name(ctx, param, value):
    def _module_exists(module_name):
        try:
            import_module(module_name)
            return True
        except ImportError:
            return False
    try:
        ast.parse(f'{value} = None')
    except:
        raise click.BadParameter(f'Not a valid name, {value}')

    if value.startswith('_'):
        raise click.BadParameter(f'Not a valid name, {value}')
    elif _module_exists(value):
        raise click.BadParameter(f'Module already existed, {value}')

    return value


def valid_log_level(ctx, param, value):
    v = value.upper()
    if v not in _nameToLevel:
        choices = ' '.join(_nameToLevel.keys())
        raise click.BadParameter(
            f'Invalid choice: {value}. (choose from {choices})')
    return v


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

    @click.command(cls=CommandFinder, context_settings=dict(obj=f'os_sanic.commands2.{scope}'))
    @click.version_option(message='%(prog)s %(version)s')
    @click.pass_context
    def cli(ctx):
        '''Command line tool for os-sanic.'''
        pass

    cli()
