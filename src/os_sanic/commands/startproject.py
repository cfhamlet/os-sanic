from os_sanic.commands import Command


class StartProjectCommand(Command):
    name = 'startproject'
    help='create new project'

    def run(self, args):
        from  os_sanic.config import create_config
        print(create_config())