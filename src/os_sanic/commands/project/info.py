import json
import os
import pickle
from base64 import b64encode
from collections import OrderedDict
from json import JSONEncoder

import click

from os_sanic.commands.project.run import create_server
from os_sanic.prototype import RouteCfg


def server_info(server):
    click.echo('Server:')
    out = json.dumps(server.sanic.config, indent=4)
    click.echo(f'{out}\n')


def apps_info(application_manager):
    apps_info = []
    for app in application_manager.apps:
        info = app_info(app)
        apps_info.append(info)

    if apps_info:
        out = json.dumps(apps_info, indent=4)
        click.echo('Applications:')
        click.echo(out)


def extensions_info(app):
    exts_info = []

    for extension in app.extension_manager.extensions:
        exts_info.append(extension.config.copy(
            update={'extension_class': str(extension.__class__)}).dict())
    return exts_info


def routes_info(app):
    routes_info = []
    for route in app.blueprint.routes:
        handler = route.handler
        config = None
        if hasattr(handler, 'view_class'):
            handler = handler.view_class
            config = handler.config.copy(update={'handler': str(handler)})
        else:
            config = RouteCfg(handler=f"<func '{handler.__module__}.{handler.__name__}'>",
                              **dict([(k, getattr(route, k))
                                      for k in RouteCfg.__fields__.keys()
                                      if hasattr(route, k) and k != 'handler']))
        routes_info.append(config.copy(
            update={'uri': route.uri,
                    'methods': list(route.methods)}).dict())
    return routes_info


def statics_info(app):
    statics_info = []
    for static in app.blueprint.statics:
        static_info = OrderedDict()
        static_info['uri'] = static.uri
        static_info['file_or_directory'] = static.file_or_directory
        static_info.update(static.kwargs)
        statics_info.append(static_info)

    return statics_info


def app_info(app):
    info = app.app_cfg.copy(
        update={'prefix': app.blueprint.url_prefix}).dict()

    for method in (extensions_info, routes_info, statics_info):
        i = method(app)
        if i:
            info[method.__name__[:-5]] = i

    return info


@click.command()
@click.option('-c', '--config-file',
              default='config.py',
              show_default=True,
              type=click.File(mode='r'),
              help='Config file')
@click.pass_context
def cli(ctx, config_file):
    '''Show config details.'''

    ctx.ensure_object(dict)

    server = create_server(ctx.obj['app'], config_file=config_file)
    server_info(server)
    apps_info(server.application_manager)
