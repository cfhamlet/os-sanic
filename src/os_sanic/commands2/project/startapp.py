import os
import os_sanic
import click
from os_sanic.commands2 import valid_name
from os_sanic.commands import create_from_tpl
from os_sanic.config import create_sanic_config


@click.command()
@click.argument('app-name', callback=valid_name)
@click.pass_context
def cli(ctx, app_name):
    '''Create new application.'''

    base_tpl_dir = os.path.join(
        os_sanic.__path__[0], 'commands2', 'template')

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
    app_package = 'apps.{}'.format(app_name)

    app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')

    config.extension_class = config.extension_name = app_name.capitalize()
    config.pattern = '/'
    config.view_class = config.extension_class + 'View'
    create_from_tpl(app_tpl_dir, app_dst_dir,
                    ignores=['*.pyc', ], **config)

    print('New os-sanic app: {}\n'.format(app_name))
    print('Use app template:')
    print('    {}\n'.format(app_tpl_dir))
    print('Create app in:')
    print('    {}\n'.format(app_dst_dir))
    print('You should add app package string into INSTALLED_APPS:')
    print('    \'{}\''.format(app_package))
