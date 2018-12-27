from argparse import FileType

from os_sanic.commands import Command, CommandScope


class ListCommand(Command):
    name = 'list'
    scope = CommandScope.PROJECT
    help = 'list installed applications'

    def add_arguments(self, parser):
        super(ListCommand, self).add_arguments(parser)

        parser.add_argument('-c', '--config',
                            help='config file (default \'.config.py\')',
                            type=FileType('rb'),
                            dest='config_file',
                            )

    def run(self, args):
        pass
