import os
import stat
import subprocess

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

import click
import json

from vcloud import client as Client, disk as Disk, vapp as VApp
from vcloud.utils import disk_partitions, wait_for_connected_disk
from .cli import cli, error, info

@cli.command(short_help='attach the volume to the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def attach(ctx,
           params,
           nodename):
    params = json.loads(params)
    try:
        is_logged_in = Client.login()
        if is_logged_in == False:
            raise Exception("Could not login to vCloud Director")
        volumeName = params['volumeName']
        disk_urn, attached_vm = Disk.find_disk(
                Disk.get_disks(Client.ctx),
                volumeName
        )
        if disk_urn is None:
            disk_urn = Disk.create_disk(
                    Client.ctx,
                    volumeName,
                    params['size'],
                    params['storage']
            )
            if disk_urn == "":
                raise Exception(
                        ("Could not create volume '%s'") % (volumeName)
                )

        volume_symlink = ("/dev/block/%s") % (disk_urn)

        if attached_vm is None:
            is_disk_attached = Disk.attach_disk(
                    Client.ctx,
                    nodename,
                    volumeName
            )
            if is_disk_attached == False:
                raise Exception(
                    ("Could not attach volume '%s' to node '%s'") % (volumeName, nodename)
                )
            is_disk_connected = wait_for_connected_disk()
            if len(is_disk_connected) == 0:
                raise Exception(
                    ("Timed out while waiting for volume '%s' to attach on node '%s'") % \
                            (volumeName, nodename)
                )
            device_name, device_status = is_disk_connected
            if os.path.lexists(volume_symlink) == False:
                os.symlink(device_name, volume_symlink)
        else:
            if os.path.lexists(volume_symlink):
                device_name = os.readlink(volume_symlink)
                try:
                    mode = os.stat(device_name).st_mode
                    assert stat.S_ISBLK(mode) == True
                except OSError:
                    raise Exception(
                        ("Device '%s' does not exist on node '%s'") % (device_name, nodename)
                    )
                except AssertionError:
                    raise Exception(
                        ("Device '%s' exists on node '%s' but is not a block device") % \
                                (device_name, nodename)
                    )
        partitions = disk_partitions(device_name.split('/')[-1])
        if len(partitions) == 0:
            try:
                # See: http://man7.org/linux/man-pages/man8/sfdisk.8.html
                cmd_create_partition = ("echo -n ',,83;' | sfdisk %s") % (device_name)
                subprocess.check_call(
                        cmd_create_partition,
                        shell=True,
                        stdout=DEVNULL,
                        stderr=DEVNULL
                )
                partition = ("%s%d") % (
                        device_name,
                        1
                )
            except subprocess.CalledProcesError:
                raise Exception(
                    ("Could not create partition on '%s'") % (device_name)
                )
        else:
            partitions.sort()
            partition = ("/%s/%s") % (
                    device_name.split('/')[1],
                    partitions[0]
            )

        success = {
            "status": "Success",
            "device": "%s" % partition
        }
        info(success)
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": "%s" % e
        }
        error(failure)
    finally:
        Client.logout()

@cli.command(short_help='wait for the volume to be attached on the remote node')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def waitforattach(ctx,
                  mountdev,
                  params):
    params = json.loads(params)
    try:
        is_logged_in = Client.login()
        if is_logged_in == False:
            raise Exception("Could not login to vCloud Director")
        volumeName = params['volumeName']
        disk_urn, attached_vm = Disk.find_disk(
                Disk.get_disks(Client.ctx),
                volumeName
        )
        if disk_urn is None:
            raise Exception(
                    ("Volume '%s' does not exist") % (mountdev)
            )

        volume_symlink = ("/dev/block/%s") % (disk_urn)

        if os.path.lexists(volume_symlink):
            device_name = os.readlink(volume_symlink)
            try:
                mode = os.stat(device_name).st_mode
                assert stat.S_ISBLK(mode) == True
            except OSError:
                raise Exception(
                    ("Device '%s' does not exist") % (device_name)
                )
            except AssertionError:
                raise Exception(
                    ("Device '%s' exists but is not a block device") % \
                            (device_name)
                )
        partitions = disk_partitions(device_name.split('/')[-1])
        if len(partitions) == 0:
            raise Exception(
                    ("Device '%s' does not have partitions") % (device_name)
            )
        else:
            partitions.sort()
            partition = ("/%s/%s") % (
                    device_name.split('/')[1],
                    partitions[0]
            )

        success = {
            "status": "Success",
            "device": "%s" % partition
        }
        info(success)
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": "%s" % e
        }
        error(failure)
    finally:
        Client.logout()

@cli.command(short_help='check the volume is attached on the node')
@click.argument('params')
@click.argument('nodename')
@click.pass_context
def isattached(ctx,
               params,
               nodename):
    attached = False
    params = json.loads(params)
    try:
        is_logged_in = Client.login()
        if is_logged_in == False:
            raise Exception("Could not login to vCloud Director")

        vm = VApp.find_vm_in_vapp(Client.ctx, nodename)
        if len(vm) > 0:
            vm = vm[0]['vm']
            volumeName = params['volumeName']
            disks = Disk.get_disks(Client.ctx)
            for disk in disks:
                if disk['name'] == volumeName \
                        and disk['attached_vm'] == vm:
                    attached = True
                    break
            success = {
                "status": "Success",
                "attached": attached
            }
            info(success)
        else:
            raise Exception(
                    "Could not find node %s" % nodename
            )
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": "%s" % e
        }
        error(failure)
    finally:
        Client.logout()
