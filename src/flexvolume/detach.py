import os
import stat

import click

from vcloud import client as Client, disk as Disk, vapp as VApp
from vcloud.utils import wait_for_connected_disk
from .cli import cli, error, info, GENERIC_SUCCESS

@cli.command(short_help='detach the volume from the node')
@click.argument('volume')
@click.argument('nodename')
@click.pass_context
def detach(ctx,
           volume,
           nodename):
    try:
        is_logged_in = Client.login()
        if is_logged_in == False:
            raise Exception("Could not login to vCloud Director")
        disk_urn, attached_vm = Disk.find_disk(
                Disk.get_disks(Client.ctx),
                volume
        )
        if disk_urn is None:
            raise Exception(
                    ("Volume '%s' does not exist") % (volume)
            )

        volume_symlink = ("/dev/block/%s") % (disk_urn)

        if attached_vm is None:
            info(GENERIC_SUCCESS)

        is_disk_detached = Disk.detach_disk(
                Client.ctx,
                nodename,
                volume
        )
        if is_disk_detached == False:
            raise Exception(
                    ("Could not detach volume '%s' from node '%s'") % \
                            (volume, nodename)
            )
        else:
            is_disk_disconnected = wait_for_connected_disk(60)
            if len(is_disk_disconnected) == 0:
                raise Exception(
                    ("Timed out while waiting for volume '%s' to detach from node '%s'") % \
                            (volume, nodename)
                )
            # Make sure task is completed
            if hasattr(is_disk_detached, 'id'):
                Client.ctx.vca.block_until_completed(is_disk_detached)

            device_name, device_status = is_disk_disconnected
            if os.path.lexists(volume_symlink):
                os.unlink(volume_symlink)

        info(GENERIC_SUCCESS)
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": "%s" % e
        }
        error(failure)
    finally:
        Client.logout()
