import json
import os
from collections import OrderedDict

import click
from os_config import Config

from os_sanic.commands.project.run import create_server


def server_info(server):
    click.echo('Server:')
    out = json.dumps(server.sanic.config, indent=4)
    click.echo(f'{out}\n')


def apps_info(server):
    am = server.app_manager
    apps_info = []
    for app in am.apps:
        info = app_info(app)
        apps_info.append(info)

    if apps_info:
        out = json.dumps(apps_info, indent=4)
        click.echo('Applications:')
        click.echo(out)


def app_info(app):
    info = OrderedDict()
    info['name'] = app.name
    info.update(Config.to_dict(app.app_cfg))

    extensions = app.extension_manager.extensions

    if extensions:
        exts_info = []
        for extension in extensions:
            ext_info = OrderedDict()
            ext_info['name'] = extension.name
            ext_info['extension_class'] = str(extension.__class__)
            ext_info.update(Config.to_dict(extension.config))
            exts_info.append(ext_info)
        if exts_info:
            info['extensions'] = exts_info

    views = app.view_manager.views
    url_prefix = app.view_manager.blueprint.url_prefix
    url_prefix = '' if not url_prefix else url_prefix
    if views:
        views_info = []
        for view in views:
            view_info = OrderedDict()
            view_info['uri'] = url_prefix+view.uri
            view_info['view_class'] = str(view.view_cls)
            view_info.update(Config.to_dict(view.config))
            views_info.append(view_info)
        if views_info:
            info['views'] = views_info

    statics = app.view_manager.statics
    if statics:
        statics_info = []
        for static in statics:
            static_info = OrderedDict()
            static_info['uri'] = static.uri
            static_info['file_or_directory'] = static.file_or_directory
            static_info.update(static.kwargs)
            statics_info.append(static_info)

        if statics_info:
            info['statics'] = statics_info

    return info


@click.command()
@click.option('-c', '--config-file', default='config.py',
              show_default=True, type=click.File(mode='r'),
              help='Config file')
@click.pass_context
def cli(ctx, config_file):
    '''Show config details.'''

    ctx.ensure_object(dict)

    server = create_server(ctx.obj['app'], config_file=config_file)
    server_info(server)
    apps_info(server)
