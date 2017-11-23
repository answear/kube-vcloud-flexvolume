import sys
import click
from .cli import cli

@cli.command(short_help='initialize the volume driver')
@click.pass_context
def init(ctx):
    pass
