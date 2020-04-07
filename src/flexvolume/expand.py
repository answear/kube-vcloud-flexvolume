import click
import json

from .cli import cli, error, info

@cli.command(short_help='expand the volume')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def expandvolume(ctx,
        params,
        mountdev,
        newsize,
        oldsize):
    params = json.loads(params)
    info(GENERIC_NOTSUPPORTED)

@cli.command(short_help='expand filesystem on attached volume')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def expandfs(ctx,
        params,
        mountdev,
        mountdir,
        newsize,
        oldsize):
    params = json.loads(params)
    info(GENERIC_NOTSUPPORTED)
