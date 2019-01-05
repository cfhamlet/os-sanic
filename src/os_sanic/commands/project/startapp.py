import os

import click

import os_sanic
from os_sanic.commands import create_from_tpl, valid_name
from os_sanic.config import create_sanic_config


@click.command()
@click.argument('app-name', callback=valid_name)
@click.pass_context
def cli(ctx, app_name):
    '''Create new application.'''

    base_tpl_dir = os.path.join(
        os_sanic.__path__[0], 'commands', 'template')

    app_dst_dir = os.path.join(os.getcwd(), f'apps/{app_name}')

    if os.path.exists(app_dst_dir):
        ctx.fail(f'App already existed, {app_dst_dir}')

    app_dir = os.path.join(os.getcwd(), 'apps')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    apps_dst_dir = os.path.join(os.getcwd(), 'apps')
    if not os.path.exists(apps_dst_dir):
        apps_tpl_dir = os.path.join(base_tpl_dir, 'apps_template')
        create_from_tpl(apps_tpl_dir, apps_dst_dir, ignores=['*.pyc', ])

    config = create_sanic_config()
    app_package = f'apps.{app_name}'

    app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')

    config.extension_class = config.extension_name = app_name.capitalize()
    config.pattern = '/'
    config.view_class = config.extension_class + 'View'
    create_from_tpl(app_tpl_dir, app_dst_dir,
                    ignores=['*.pyc', ], **config)

    click.echo(f'New os-sanic app: {app_name}\n')
    click.echo('Use app template:')
    click.echo(f'    {app_tpl_dir}\n')
    click.echo('Create app in:')
    click.echo(f'    {app_dst_dir}\n')
    click.echo('You should add app package string into INSTALLED_APPS:')
    click.echo(f'    \'{app_package}\'')
