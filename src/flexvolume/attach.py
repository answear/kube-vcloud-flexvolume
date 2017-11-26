import os
import stat

import click
import json
import pyudev

from functools import partial 

from vcloud import client as Client, disk as Disk, vapp as VApp
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
    params = json.loads(params)
    try:
        is_logged_in = Client.login()
        if is_logged_in == False:
            raise Exception("Could not login to vCloud Director")
        volumeName = params['volumeName']
        find_disk = \
            lambda x, disk: next(([i['id'], i['attached_vm']] for i in x if i['name'] == disk), None)
        is_disk_exist = find_disk(
                Disk.get_disks(Client.ctx),
                volumeName
        )
        if is_disk_exist is None:
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
        else:
            disk_urn, attached_vm = is_disk_exist

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
            os.symlink(device_name, volume_symlink)
        else:
            if os.path.lexists(volume_symlink):
                device_name = os.readlink(volume_symlink)
                try:
                    mode = os.stat(device_name).st_mode
                    assert stat.S.ISBLK(mode) == True
                except OSError:
                    raise Exception(
                        ("Device '%s' does not exist on node '%s'") % (device_name, nodename)
                    )
                except AssertionError:
                    raise Exception(
                        ("Device '%s' exists on node '%s' but is not a block device") % \
                                (device_name, nodename)
                    )
        success = {
            "status": "Success",
            "device": "%s" % device_name
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

def wait_for_connected_disk(timeout=600):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='disk')

    result = []
    for device in iter(partial(monitor.poll, timeout), None):
        if device.action == 'add':
            result = [device.device_node, 'connected']
            break
        elif device.action == 'remove':
            result = [device.device_node, 'disconnected']
            break
    return result

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
