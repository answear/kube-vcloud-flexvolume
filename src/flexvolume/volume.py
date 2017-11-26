import click
import json

from .cli import cli, error, info

@cli.command(short_help='get the volume name')
@click.argument('params')
@click.pass_context
def getvolumename(
        ctx,
        params):
    params = json.loads(params)
    success = {
        "status": "Success",
        "message": "Not supported"
    }
    info(success)
