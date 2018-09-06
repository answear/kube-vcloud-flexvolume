import os
import stat
import sys

from etcd3autodiscover import Etcd3Autodiscover
from decimal import Decimal

import click

from pyvcloud.vcd.client import TaskStatus
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
    config = Client.ctx.config
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

        volume_symlink = ("block/%s") % (disk_urn)
        volume_symlink_full = ("/dev/%s") % (volume_symlink)

        if os.path.lexists(volume_symlink_full):
            device_name = os.readlink(volume_symlink_full)
            device_name_short = device_name.split('/')[-1]
        if attached_vm is None:
            info(GENERIC_SUCCESS)

        etcd = Etcd3Autodiscover(host=config['etcd']['host'],
                                 port=config['etcd']['port'],
                                 ca_cert=config['etcd']['ca_cert'],
                                 cert_key=config['etcd']['key'],
                                 cert_cert=config['etcd']['cert'],
                                 timeout=config['etcd']['timeout'])
        client = etcd.connect()
        if client is None:
            raise Exception(
                    ("Could not connect to etcd server '%s'") % (etcd.errstr())
            )
        lock_name = ("vcloud/%s/disk/detach") % (nodename)
        lock_ttl = 120
        with client.lock(lock_name, ttl=lock_ttl) as lock:
            n = 0
            absolute = 10
            while lock.is_acquired() == False and n < 6:
                timeout = round(Decimal(4 * 1.29 ** n))
                absolute += timeout
                n += 1
                lock.acquire(timeout=timeout)

            if lock.is_acquired() == False:
                raise Exception(
                        ("Could not acquire lock after %0.fs. Giving up") % (absolute)
                )
            lock.refresh()
            is_disk_detached = Disk.detach_disk(
                    Client.ctx,
                    nodename,
                    volume
            )
            is_disk_disconnected = []
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
                task = Client.ctx.client.get_task_monitor().wait_for_status(
                    task=is_disk_detached,
                    timeout=60,
                    poll_frequency=2,
                    fail_on_statuses=None,
                    expected_target_statuses=[
                        TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                        TaskStatus.CANCELED
                    ],
                    callback=None)
                assert task.get('status') == TaskStatus.SUCCESS.value
        lock.release()
        info(GENERIC_SUCCESS)
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": (
                    ("Error on line %d in file %s (%s): %s") % 
                    (sys.exc_info()[-1].tb_lineno, sys.exc_info()[-1].tb_frame.f_code.co_filename, type(e).__name__, e)
            )
        }
        error(failure)
    finally:
        if len(is_disk_disconnected) == 2:
            device_status = is_disk_disconnected[1]
            if device_status == 'disconnected':
                if os.path.lexists(volume_symlink_full):
                    os.unlink(volume_symlink_full)
                udev_rule_path = ("/etc/udev/rules.d/90-independent-disk-%s.rules") % (device_name_short)
                if os.path.exists(udev_rule_path):
                    os.unlink(udev_rule_path)
        Client.logout()
