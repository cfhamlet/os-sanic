import os

import click

import os_sanic
from os_sanic.commands import create_from_tpl, valid_name
from os_sanic.config import create


def app_creation_params(app_name, base_path=None):
    app_package = f'apps.{app_name}'

    base_tpl_dir = os.path.join(
        os_sanic.__path__[0], 'commands', 'template')

    app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')

    b = base_path if base_path is not None else os.getcwd()
    app_dst_dir = os.path.join(b, 'apps', f'{app_name}')

    return app_package, app_tpl_dir, app_dst_dir


def create_app(ctx, app_name, app_package, app_tpl_dir, app_dst_dir, **kwargs):

    if os.path.exists(app_dst_dir):
        ctx.fail(f'App already existed, {app_dst_dir}')

    apps_tpl_dir = app_tpl_dir.replace('app_template', 'apps_template')
    apps_dst_dir = app_dst_dir[0:app_dst_dir.rfind(app_name)]

    if not os.path.exists(apps_dst_dir):
        create_from_tpl(apps_tpl_dir, apps_dst_dir, ignores=['*.pyc', ])

    config = create()
    config.app_name = app_name
    config.extension_class = config.extension_name = app_name.capitalize()
    config.uri = '/'
    config.view_class = config.extension_class + 'View'

    ignores = ['*.pyc']

    config.full_feature = kwargs.get('full_feature', False)
    if not config.full_feature:
        ignores.extend(['middleware.py-tpl', 'exception.py-tpl'])
    create_from_tpl(app_tpl_dir, app_dst_dir,
                    ignores=ignores, **config)


@click.command()
@click.argument('app-name', callback=valid_name)
@click.option('--full-feature', is_flag=True,  help='Create app with full feature.')
@click.pass_context
def cli(ctx, app_name, full_feature):
    '''Create new application.'''

    app_package, app_tpl_dir, app_dst_dir = app_creation_params(app_name)
    create_app(ctx, app_name, app_package, app_tpl_dir,
               app_dst_dir, full_feature=full_feature)

    click.echo(f'New os-sanic app: {app_name}\n')
    click.echo('Use app template:')
    click.echo(f'    {app_tpl_dir}\n')
    click.echo('Create app in:')
    click.echo(f'    {app_dst_dir}\n')
    click.echo('Please add app package into INSTALLED_APPS:')
    click.echo(f'    \'{app_package}\'')
