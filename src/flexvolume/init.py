import click
import json

from .cli import cli, error, info

@cli.command(short_help='initialize the volume driver')
@click.pass_context
def init(ctx):
    result = {
        "status": "Success",
        "capabilities": {
            "attach": True
        }
    }
    info(json.dumps(result))
