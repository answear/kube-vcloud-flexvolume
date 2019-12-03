import click

from .cli import cli, error, info

@cli.command(short_help='initialize the volume driver')
@click.pass_context
def init(ctx):
    success = {
        "status": "Success",
        "capabilities": {
            "attach": True,
            "requiresFSResize": False
        }
    }
    info(success)
