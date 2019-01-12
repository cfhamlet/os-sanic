import os

import click

from os_sanic.commands import valid_log_level
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.server import Server

default_config = create_sanic_config(load_env=SANIC_ENV_PREFIX)


@click.command()
@click.option('--access-log', is_flag=True, help='Enable access log.')
@click.option('--debug', is_flag=True, help='Enable debug mode.')
@click.option('-c', '--config',
              default='config.py', show_default=True,
              type=click.File(mode='r'), help='Config file.')
@click.option('-h', '--host',
              default=default_config.get('HOST'),
              show_default=True, help='Bind address.')
@click.option('-p', '--port',
              default=default_config.get('PORT'),
              show_default=True, help='Listen port.')
@click.option('-l', '--log-level', metavar='LOG_LEVEL',
              default=default_config.get('LOG_LEVEL'), show_default=True,
              callback=valid_log_level,
              help='Log level.'
              )
@click.pass_context
def cli(ctx, **kwargs):
    '''Run server.'''

    ctx.ensure_object(dict)

    config_file = os.path.abspath(kwargs.get('config').name)

    server = Server.create(
        ctx.obj['app'],
        config_file=config_file,
        log_config=ctx.obj.get('log_config', None),
        **dict([(k.upper(), v) for k, v in kwargs.items()]),
    )

    server.run()
