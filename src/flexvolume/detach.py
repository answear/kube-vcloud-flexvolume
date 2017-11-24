import click

from .cli import cli, error, info

@cli.command(short_help='detach the volume from the node')
@click.argument('mountdev')
@click.argument('nodename')
@click.pass_context
def detach(ctx,
           mountdev,
           nodename):
    # TODO:
    # 1. Determine which disk we should detach (by looking symlinks in /dev/block)
    # 2. Login to vCloud
    # 3. Detach disk from node
    pass
