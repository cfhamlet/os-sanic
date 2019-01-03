import os
import json
import pprint
from argparse import FileType

from os_sanic.commands import Command, CommandScope
from os_sanic.server import Server
from os_config import Config
from os_sanic.utils import left_align


class InfoCommand(Command):
    name = 'info'
    scope = CommandScope.PROJECT
    help = 'show config information'

    def add_arguments(self, parser):
        super(InfoCommand, self).add_arguments(parser)

        parser.add_argument('-c', '--config',
                            help='config file (default \'.config.py\')',
                            type=FileType('rb'),
                            dest='config_file',
                            )

    def process_arguments(self, args):
        config_file = args.config_file
        if config_file:
            config_file = os.path.abspath(config_file.name)
        else:
            config_file = os.path.join(os.getcwd(), 'config.py')

        kwargs = {}
        for k, v in args._get_kwargs():
            if v:
                kwargs[k.upper()] = v
        self._server = Server.create(
            'os-sanic',
            config_file=config_file,
            **kwargs,
        )

    def _server_info(self, args):
        print('Server:')

        out = json.dumps(self._server.sanic.config, indent=4)
        print('{}\n'.format(out))

    def _app_info(self, args, app):
        print('    {}: <package {}>'.format(app.name, app.package))
        extensions = app.extension_manager.extensions

        if extensions:
            print('    Extensions:')
            for extension in extensions:
                print('        {}: {}'.format(
                    extension.name, extension.__class__))
                if len(extension.config) > 0:
                    print(left_align(Config.to_json(
                        extension.config, indent=4), align=8))

        views = app.view_manager.views
        url_prefix = app.view_manager.blueprint.url_prefix
        url_prefix = '' if not url_prefix else url_prefix
        if views:
            print('    Views:')
            for view in views:
                print('        {} {}'.format(
                    url_prefix + view.pattern, view.view_cls))
                if len(view.config) > 0:
                    print(left_align(Config.to_json(
                        view.config, indent=4), align=8))

    def _apps_info(self, args):
        am = self._server.app_manager
        print('Applications:')
        for app in am.apps:
            self._app_info(args, app)
            print('\n')

    def run(self, args):
        self._server_info(args)
        self._apps_info(args)
