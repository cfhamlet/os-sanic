from enum import Enum

CommandScope = Enum('CommandScoe', 'GLOBAL, PROJECT')


class Command(object):

    scope = CommandScope.GLOBAL
    name = None
    description = ''
    help = ''

    def add_arguments(self, parser):
        pass

    def process_arguments(self, args):
        pass

    def run(self, args):
        pass
