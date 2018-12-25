import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import os_sanic
from os_sanic.commands import Command, CommandScope
from os_sanic.utils import iter_classes, walk_modules


def _usage(command=None):
    usage_string = '\r%(prog)s {version}\n\nUsage: %(prog)s '
    if command is None:
        usage_string += '[OPTIONS] COMMAND'
    else:
        usage_string += '{command} [OPTIONS]'

    return usage_string.format(
        version=os_sanic.__version__,
        command=command,
    )


def _create_argparser():
    parser = ArgumentParser(
        description='Command line tool for os-sanic',
        usage=_usage(),
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(
                            version=os_sanic.__version__)
                        )

    return parser


def find_commands(cmd_module_path, scope=None):
    cmds = {}
    for cmd_module in walk_modules(cmd_module_path):
        for cmd_cls in iter_classes(cmd_module.__name__, Command):
            if not scope or scope == cmd_cls.scope:
                cmds[cmd_cls.name] = cmd_cls()
    return cmds


def load_subparser(parser, commands):
    subparser = parser.add_subparsers(
        title='Commands',
        dest='command'
    )
    for name, cmd in commands.items():
        cmd_parser = subparser.add_parser(
            cmd.name,
            prog=parser.prog,
            description=cmd.description if cmd.description
            else cmd.help.capitalize(),
            help=cmd.help,
            usage=_usage(command=name),
            conflict_handler='resolve',
        )
        cmd.add_arguments(cmd_parser)


def execute(argv=None, scope='global'):
    argv = argv or sys.argv[1:]
    scope = CommandScope[scope.upper()]

    parser = _create_argparser()
    commands = find_commands('os_sanic.commands', scope)

    load_subparser(parser, commands)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    command = commands[args.command]
    command.process_arguments(args)
    command.run(args)


if __name__ == '__main__':
    execute()
