import click

from .cli import cli, error, info

@cli.command(short_help='detach the volume from the node')
@click.argument('mountdev')
@click.argument('nodename')
@click.pass_context
def detach(ctx,
           mountdev,
           nodename):
    pass
