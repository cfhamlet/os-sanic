import os
import io

import click

from os_sanic.commands import valid_log_level
from os_sanic.config import SANIC_ENV_PREFIX, create
from os_sanic.server import Server


def create_server(app, **kwargs):
    config_file = kwargs.get('config_file', None)
    if config_file and isinstance(config_file, io.TextIOWrapper):
        config_file = config_file.name

    config = create(load_env=SANIC_ENV_PREFIX)
    if config_file:
        config_file = os.path.abspath(config_file)
        kwargs['config_file'] = config_file
        config.from_pyfile(config_file)
    config.update(dict([(k.upper(), v) for k, v in kwargs.items()])),

    server = Server.create(
        app,
        config=config,
        env_prefix=SANIC_ENV_PREFIX,
    )
    return server


default_config = create(load_env=SANIC_ENV_PREFIX)


@click.command()
@click.option('--access-log', is_flag=True,  help='Enable access log.')
@click.option('--debug', is_flag=True,  help='Enable debug mode.')
@click.option('-c', '--config-file',
              default='config.py', show_default=True,
              type=click.File(mode='r'), help='Config file.')
@click.option('-h', '--host',
              show_default=True, help=f'Bind address. [default: {default_config.get("HOST")}]')
@click.option('-p', '--port',
              show_default=True, help=f'Listen port. [default: {default_config.get("PORT")}]')
@click.option('-l', '--log-level', metavar='LOG_LEVEL',
              show_default=True,
              callback=valid_log_level,
              help=f'Log level. [default: {default_config.get("LOG_LEVEL")}]'
              )
@click.pass_context
def cli(ctx, **kwargs):
    '''Run server.'''

    ctx.ensure_object(dict)

    kwargs = dict([(k, v) for k, v in kwargs.items() if v])

    server = create_server(ctx.obj['app'], **kwargs)
    server.run()
