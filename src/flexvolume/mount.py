import sys
import click
from .cli import cli

@cli.command(short_help='mount the device to a global path')
@click.argument('mountdir')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def mountdevice(ctx,
                mountdir,
                mountdev,
                params):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
        sys.exit(-1)

@cli.command(short_help='unmount the global mount for the device')
@click.argument('mountdir')
@click.pass_context
def unmountdevice(ctx,
                  mountdir):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
        sys.exit(-1)
