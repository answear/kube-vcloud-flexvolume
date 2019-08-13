import os
import sys

import click

from pyvcloud.vcd.client import TaskStatus
from vcloud import client as Client, disk as Disk
from .cli import cli, error, info, GENERIC_SUCCESS

@cli.command(short_help='delete the volume')
@click.argument('volume')
@click.pass_context
def delete(ctx,
           volume):
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

        if attached_vm is not None:
            raise Exception(
                    ("Could not delete attached volume '%s'") % (volume)

        is_disk_deleted = Disk.delete_disk(
                Client.ctx,
                volume
        )
        if not is_disk_deleted:
            raise Exception(
                    ("Could not delete volume '%s'") % (volume)
                )
        else:
            # Make sure task is completed
            task = Client.ctx.client.get_task_monitor().wait_for_status(
                task=is_disk_deleted[0],
                timeout=60,
                poll_frequency=2,
                fail_on_statuses=None,
                expected_target_statuses=[
                    TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                    TaskStatus.CANCELED
                ],
                callback=None)
            assert task.get('status') == TaskStatus.SUCCESS.value
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
        Client.logout()
