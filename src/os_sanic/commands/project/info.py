import json
import os

import click
from os_config import Config

from os_sanic.server import Server
from os_sanic.utils import left_align


def server_info(server):
    click.echo('Server:')

    out = json.dumps(server.sanic.config, indent=4)
    click.echo(f'{out}\n')


def apps_info(server):
    am = server.app_manager
    click.echo('Applications:')
    for app in am.apps:
        app_info(app)
        click.echo('\n')


def app_info(app):
    click.echo(f'    {app.name}: <package \'{app.package}\'>')
    extensions = app.extension_manager.extensions

    if extensions:
        click.echo('    Extensions:')
        for extension in extensions:
            click.echo(f'        {extension.name}: {extension.__class__}')
            if len(extension.config) <= 0:
                continue
            click.echo(left_align(Config.to_json(
                extension.config, indent=4), align=8))

    views = app.view_manager.views
    url_prefix = app.view_manager.blueprint.url_prefix
    url_prefix = '' if not url_prefix else url_prefix
    if views:
        click.echo('    Views:')
        for view in views:
            click.echo(f'        {url_prefix+view.pattern} {view.view_cls}')
            if len(view.config) <= 0:
                continue
            click.echo(left_align(Config.to_json(
                view.config, indent=4), align=8))


@click.command()
@click.option('-c', '--config', default='config.py',
              show_default=True, type=click.File(mode='r'),
              help='Config file')
def cli(config):
    '''Show config details.'''
    config_file = os.path.abspath(config.name)
    server = Server.create(
        'os-sanic',
        config_file=config_file,
    )

    server_info(server)
    apps_info(server)
