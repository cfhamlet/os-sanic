import os

import click

from os_sanic.commands import valid_log_level
from os_sanic.config import create_sanic_config
from os_sanic.server import Server


def create_server(app, **kwargs):
    config_file = os.path.abspath(kwargs.get('config_file').name)
    kwargs['config_file'] = config_file

    config = create_sanic_config()
    config.from_pyfile(config_file)
    config.update(dict([(k.upper(), v) for k, v in kwargs.items()])),

    server = Server.create(
        app,
        config=config,
    )
    return server


default_config = create_sanic_config()


@click.command()
@click.option('--access-log', is_flag=True, help='Enable access log.')
@click.option('--debug', is_flag=True, help='Enable debug mode.')
@click.option('-c', '--config-file',
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

    server = create_server(ctx.obj['app'], **kwargs)
    server.run()
