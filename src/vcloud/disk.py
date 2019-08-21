import vcloud.client as Client

from pyvcloud.vcd.client import TaskStatus
from pyvcloud.vcd.client import VCLOUD_STATUS_MAP
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.utils import extract_id
from vcloud.vapp import find_vm_in_vapp
from vcloud.utils import size_to_bytes, bytes_to_size

def find_disk(ctx, name):
    try:
        disk = ctx.vdc.get_disk(name)
        disk_id = extract_id(disk.get('id'))
        attached_vm = None
        if hasattr(disk, 'attached_vms') and hasattr(disk.attached_vms, 'VmReference'):
            attached_vm = disk.attached_vms.VmReference.get('href').split('/vm-')[-1]
        return [disk_id, attached_vm]
    except Exception as e:
        return [None, None]

def create_disk(ctx, name, size, storage_profile_name, bus_type=None, bus_sub_type=None):
    """
    Create an independent disk volume

    :param name: (str): The name of the new disk
    :param size: (str): The size of the new disk in string format (e.g. 100Mi, 2Gi)
    :param storage_profile_name: (str): The name of the storage profile where a created disk will be attached
    :return (str): The disk identifier on success, or empty string on failure
    """
    try:
        size = size_to_bytes(size)
        if size == 0:
            raise
        disk_resource = ctx.vdc.create_disk(
                name=name,
                size=size,
                storage_profile_name=storage_profile_name,
                bus_type=str(bus_type),
                bus_sub_type=bus_sub_type
        )
        task = ctx.client.get_task_monitor().wait_for_status(
            task=disk_resource.Tasks.Task[0],
            timeout=60,
            poll_frequency=2,
            fail_on_statuses=None,
            expected_target_statuses=[
                TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                TaskStatus.CANCELED
            ],
            callback=None)

        assert task.get('status') == TaskStatus.SUCCESS.value
        disk_id = extract_id(disk_resource[0].get('id'))
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            return ""
    return disk_id

def delete_disk(ctx, name):
    result = []
    try:
        disks = get_disks(ctx)
        for disk in disks:
            if disk['name'] == name:
                ctx.vdc.delete_disk(
                        name,
                        disk['id']
                )
                result.append(disk['id'])
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return result

def attach_disk(ctx, vm_name, disk_name, block=False):
    try:
        vm = find_vm_in_vapp(ctx, vm_name=vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vdc.get_vapp(vm['vapp_name'])
            the_vapp = VApp(ctx.client, vm['vapp_name'], resource=vapp)
            disks = get_disks(ctx)
            for disk in disks:
                if disk['name'] == disk_name:
                    result = the_vapp.attach_disk_to_vm(disk['href'], vm['vm_name'])
                    if block == True:
                        task = ctx.client.get_task_monitor().wait_for_status(
                            task=result,
                            timeout=60,
                            poll_frequency=2,
                            fail_on_statuses=None,
                            expected_target_statuses=[
                                TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                                TaskStatus.CANCELED
                            ],
                            callback=None)
                        assert task.get('status') == TaskStatus.SUCCESS.value
                        return True
                    else:
                        return result
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return False

def detach_disk(ctx, vm_name, disk_name, block=False):
    try:
        vm = find_vm_in_vapp(ctx, vm_name=vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vdc.get_vapp(vm['vapp_name'])
            the_vapp = VApp(ctx.client, vm['vapp_name'], resource=vapp)
            disks = get_disks(ctx)
            for disk in disks:
                if disk['name'] == disk_name:
                    result = the_vapp.detach_disk_from_vm(disk['href'], vm['vm_name'])
                    if block == True:
                        task = ctx.client.get_task_monitor().wait_for_status(
                            task=result,
                            timeout=60,
                            poll_frequency=2,
                            fail_on_statuses=None,
                            expected_target_statuses=[
                                TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                                TaskStatus.CANCELED
                            ],
                            callback=None)
                        assert task.get('status') == TaskStatus.SUCCESS.value
                        return True
                    else:
                        return result
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return False

def get_disks(ctx):
    result = []
    try:
        disks = ctx.vdc.get_disks()
        for disk in disks:
            disk_id = extract_id(disk.get('id'))
            attached_vm = None
            attached_vm_href = None
            if hasattr(disk, 'attached_vms') and hasattr(disk.attached_vms, 'VmReference'):
                attached_vm = disk.attached_vms.VmReference.get('name')
                attached_vm_href = disk.attached_vms.VmReference.get('href')
            result.append(
                {
                    'name': disk.get('name'),
                    'id': disk_id,
                    'href': disk.get('href'),
                    'storage_profile': disk.StorageProfile.get('name'),
                    'storage_profile_href': disk.StorageProfile.get('href'),
                    'bus_type': int(disk.get('busType')),
                    'bus_sub_type': disk.get('busSubType'),
                    'size_bytes': int(disk.get('size')),
                    'size_human': bytes_to_size(
                            int(disk.get('size'))
                    ),
                    'status': VCLOUD_STATUS_MAP.get(int(disk.get('status'))),
                    'attached_vm': attached_vm,
                    'attached_vm_href': attached_vm_href,
                    'vdc': extract_id(ctx.vdc.resource.get('id'))
                }

            )
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return result
