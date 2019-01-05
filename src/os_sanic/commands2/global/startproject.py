import click
import os_sanic
import sys
import os
from os_sanic.config import create_sanic_config

from os_sanic.commands import create_from_tpl
from os_sanic.commands2 import valid_name


@click.command()
@click.argument('project-name', callback=valid_name)
@click.pass_context
def cli(ctx, project_name):
    '''Create new project.'''

    base_tpl_dir = os.path.join(
        os_sanic.__path__[0], 'commands2', 'template')

    proj_tpl_dir = os.path.join(base_tpl_dir, 'project_template')

    proj_dst_dir = os.path.join(os.getcwd(), project_name)

    if os.path.exists(proj_dst_dir):
        ctx.fail(f'Project already existed, {proj_dst_dir}')

    config = create_sanic_config()
    config.app_name = project_name
    config.app_package = 'apps.{}'.format(project_name)

    create_from_tpl(proj_tpl_dir, proj_dst_dir,
                    ignores=['*.pyc', ], **config)

    apps_tpl_dir = os.path.join(base_tpl_dir, 'apps_template')
    apps_dst_dir = os.path.join(proj_dst_dir, 'apps')
    create_from_tpl(apps_tpl_dir, apps_dst_dir, ignores=['*.pyc', ])

    app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')
    app_dst_dir = os.path.join(
        proj_dst_dir, 'apps/{}'.format(project_name))

    config.extension_class = config.extension_name = project_name.capitalize()
    config.pattern = '/'
    config.view_class = config.extension_class + 'View'
    create_from_tpl(app_tpl_dir, app_dst_dir,
                    ignores=['*.pyc', ], **config)

    click.echo(f'New os-sanic project: {project_name}\n')
    click.echo('Use project template:')
    click.echo(f'    {proj_tpl_dir}')
    click.echo('Use app template:')
    click.echo(f'    {app_tpl_dir}\n')
    click.echo('Create project in:')
    click.echo(f'    {proj_dst_dir}')
    click.echo('Create app in:')
    click.echo(f'    {app_dst_dir}\n')
    click.echo('You can start your server with:')
    click.echo(f'    cd {proj_dst_dir}')
    click.echo('    python manager.py run')
