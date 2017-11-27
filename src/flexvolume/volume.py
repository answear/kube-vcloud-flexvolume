import click
import json

from .cli import cli, error, info, GENERIC_NOTSUPPORTED

@cli.command(short_help='get the volume name')
@click.argument('params')
@click.pass_context
def getvolumename(
        ctx,
        params):
    params = json.loads(params)
    info(GENERIC_NOTSUPPORTED)
