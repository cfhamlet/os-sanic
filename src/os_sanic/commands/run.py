import os
from argparse import FileType
from logging import _nameToLevel

from os_sanic.commands import Command, CommandScope
from os_sanic.config import SANIC_ENV_PREFIX, create_sanic_config
from os_sanic.sanic_server import Server


class RunCommand(Command):
    name = 'run'
    # scope = CommandScope.PROJECT
    help = 'run server'

    def __init__(self):
        self._default_config = create_sanic_config(load_env=SANIC_ENV_PREFIX)

    def add_arguments(self, parser):
        super(RunCommand, self).add_arguments(parser)

        parser.add_argument('--access-log',
                            help='enable access log',
                            action='store_true',
                            dest='access_log',
                            )

        dft_address = self._default_config.get('HOST')
        parser.add_argument('-h', '--host',
                            help='bind address (default: {address})'.format(
                                address=dft_address),
                            dest='host',
                            )

        dft_port = self._default_config.get('PORT')
        parser.add_argument('-p', '--port',
                            help='listen port (default: {port})'.format(
                                port=dft_port),
                            type=int,
                            dest='port',
                            )

        parser.add_argument('-c', '--config',
                            help='config file (default \'.config.py\')',
                            type=FileType('rb'),
                            dest='config_file',
                            )

        parser.add_argument('--debug',
                            help='enable debug mode',
                            action='store_true',
                            dest='debug',
                            )

        dft_log_level = self._default_config.get('LOG_LEVEL')
        parser.add_argument('-l', '--log-level',
                            help='log level (default {log_level})'.format(
                                log_level=dft_log_level),
                            metavar='LOG_LEVEL',
                            type=lambda s: s.upper(),
                            choices=_nameToLevel.keys(),
                            dest='log_level',
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

    def run(self, args):
        self._server.run()
