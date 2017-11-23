import sys
import click
from .cli import cli

@cli.command(short_help='detach the volume from the node')
@click.argument('mountdev')
@click.argument('nodename')
@click.pass_context
def detach(ctx,
           mountdev,
           nodename):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
        sys.exit(-1)
