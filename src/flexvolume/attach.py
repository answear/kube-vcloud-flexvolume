import click

from vcloud.client import *
from vcloud.disk import *
from .cli import cli, error, info

@cli.command(short_help='attach the volume to the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def attach(ctx,
           params,
           nodename):
    # TODO:
    # 1. Login to vCloud
    # 2. Find disks with given name
    # 3. Create disk if not exists
    # 4. Attach to node
    pass

@cli.command(short_help='wait for the volume to be attached on the remote node')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def waitforattach(ctx,
                  mountdev,
                  params):
    # TODO:
    # 1. Observe udev events (ACTION="add", SUBSYSTEM="block", TYPE="disk")
    # 2. Create symlink pointing to device under /dev/block (eg. /dev/block/mysql -> /dev/sdb)
    # 3. Create one big partition if not exists
    pass

@cli.command(short_help='check the volume is attached on the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def isattached(ctx,
               params,
               nodename):
    # TODO:
    # 1. Login to vCloud
    # 2. Check if disk is attached
    pass
