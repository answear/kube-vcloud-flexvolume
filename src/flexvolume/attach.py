import sys
import click
from .cli import cli

@cli.command(short_help='attach the volume to the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def attach(ctx,
           params,
           nodename):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
        sys.exit(-1)

@cli.command(short_help='wait for the volume to be attached on the remote node')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def waitforattach(ctx,
                  mountdev,
                  params):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
       sys.exit(-1)

@cli.command(short_help='check the volume is attached on the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def isattached(ctx,
               params,
               nodename):
    try:
        print(ctx.invoked_subcommand)
    except Exception as e:
        sys.exit(-1)
