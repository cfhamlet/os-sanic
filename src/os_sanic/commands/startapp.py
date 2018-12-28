import os
import sys

import os_sanic
from os_sanic.cmdline import _usage
from os_sanic.commands import (Command, CommandScope, create_from_tpl,
                               valid_name)
from os_sanic.config import create_sanic_config

APP_NAME = 'APPNAME'


class StartAppCommand(Command):
    name = 'startapp'
    scope = CommandScope.PROJECT
    help = 'create new application'
    usage = _usage('startapp', [APP_NAME])

    def add_arguments(self, parser):
        super(StartAppCommand, self).add_arguments(parser)

        parser.add_argument('app_name',
                            metavar=APP_NAME,
                            help='app name',
                            )

    def run(self, args):
        try:
            valid_name(args.app_name)
        except Exception as e:
            print('Error: {}'.format(e))
            sys.exit(1)

        base_tpl_dir = os.path.join(
            os_sanic.__path__[0], 'commands')

        app_dst_dir = os.path.join(
            os.getcwd(), 'apps/{}'.format(args.app_name))

        if os.path.exists(app_dst_dir):
            print('Error: already existed, {}'.format(app_dst_dir))
            sys.exit(1)

        app_dir = os.path.join(os.getcwd(), 'apps')
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)

        apps_dst_dir = os.path.join(os.getcwd(), 'apps')
        if not os.path.exists(apps_dst_dir):
            apps_tpl_dir = os.path.join(base_tpl_dir, 'apps_template')
            create_from_tpl(apps_tpl_dir, apps_dst_dir, ignores=['*.pyc', ])

        config = create_sanic_config()
        app_package = 'apps.{}'.format(args.app_name)

        app_tpl_dir = os.path.join(base_tpl_dir, 'app_template')

        config.extension_class = config.extension_name = args.app_name.capitalize()
        config.pattern = '/'
        config.view_class = config.extension_class + 'View'
        create_from_tpl(app_tpl_dir, app_dst_dir,
                        ignores=['*.pyc', ], **config)

        print('New os-sanic app: {}\n'.format(args.app_name))
        print('Use app template:')
        print('    {}\n'.format(app_tpl_dir))
        print('Create app in:')
        print('    {}\n'.format(app_dst_dir))
        print('You should add app package string into INSTALLED_APPS:')
        print('    \'{}\''.format(app_package))
