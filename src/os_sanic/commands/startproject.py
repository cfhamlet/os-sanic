import os
import sys

import os_sanic
from os_sanic.cmdline import _usage
from os_sanic.commands import Command, create_from_tpl, valid_name
from os_sanic.config import create_sanic_config

PRJ_NAME = 'PROJECTNAME'


class StartProjectCommand(Command):
    name = 'startproject'
    help = 'create new project'
    usage = _usage('startproject', [PRJ_NAME])

    def add_arguments(self, parser):
        super(StartProjectCommand, self).add_arguments(parser)

        parser.add_argument('project_name',
                            metavar=PRJ_NAME,
                            help='project name',
                            )

    def run(self, args):
        try:
            valid_name(args.project_name)
        except Exception as e:
            print('Error: {}'.format(e))
            sys.exit(1)

        base_tpl_dir = os.path.join(
            os_sanic.__path__[0], 'commands')

        proj_tpl_dir = os.path.join(base_tpl_dir, 'project_template')

        proj_dst_dir = os.path.join(os.getcwd(), args.project_name)

        if os.path.exists(proj_dst_dir):
            print('Error: already existed, {}'.format(proj_dst_dir))
            sys.exit(1)

        config = create_sanic_config()
        config.app_name = args.project_name
        config.app_package = 'apps.{}'.format(args.project_name)

        create_from_tpl(proj_tpl_dir, proj_dst_dir,
                        ignores=['*.pyc', ], **config)

        apps_tpl_dir = os.path.join(base_tpl_dir, 'apps_template')
        apps_dst_dir = os.path.join(proj_dst_dir, 'apps')
        create_from_tpl(apps_tpl_dir, apps_dst_dir, ignores=['*.pyc', ])

        app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')
        app_dst_dir = os.path.join(
            proj_dst_dir, 'apps/{}'.format(args.project_name))

        config.extension_class = config.extension_name = args.project_name.capitalize()
        config.pattern = '/'
        config.view_class = config.extension_class + 'View'
        create_from_tpl(app_tpl_dir, app_dst_dir,
                        ignores=['*.pyc', ], **config)

        print('New os-sanic project: {}\n'.format(args.project_name))
        print('Use project template:')
        print('    {}'.format(proj_tpl_dir))
        print('Use app template:')
        print('    {}\n'.format(app_tpl_dir))
        print('Create project in:')
        print('    {}'.format(proj_dst_dir))
        print('Create app in:')
        print('    {}\n'.format(app_dst_dir))
        print('You can start your server with:')
        print('    cd {}'.format(proj_dst_dir))
        print('    python manager.py run')
