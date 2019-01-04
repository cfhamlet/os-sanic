import click


@click.command()
@click.option('--access-log', is_flag=True)
@click.option('-c', '--config', default='config.py',
              show_default=True, type=click.File(mode='r'),
              help='Config file')
def cli(config, access_log):
    print(config)
    print(access_log)
