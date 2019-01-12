import os
import sys

import click

import os_sanic
from os_sanic.commands import create_from_tpl, valid_name
from os_sanic.commands.project.startapp import app_creation_params, create_app
from os_sanic.config import create_sanic_config


@click.command()
@click.argument('project-name', callback=valid_name)
@click.pass_context
def cli(ctx, project_name):
    '''Create new project.'''

    base_tpl_dir = os.path.join(
        os_sanic.__path__[0], 'commands', 'template')

    proj_tpl_dir = os.path.join(base_tpl_dir, 'project_template')

    proj_dst_dir = os.path.join(os.getcwd(), project_name)

    if os.path.exists(proj_dst_dir):
        ctx.fail(f'Project already existed, {proj_dst_dir}')

    config = create_sanic_config()
    config.project_name = project_name

    app_package, app_tpl_dir, app_dst_dir = app_creation_params(
        project_name, proj_dst_dir)

    config.app_name = project_name
    config.app_package = app_package

    create_from_tpl(proj_tpl_dir, proj_dst_dir,
                    ignores=['*.pyc', ], **config)

    create_app(ctx, project_name, app_package, app_tpl_dir, app_dst_dir)

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
