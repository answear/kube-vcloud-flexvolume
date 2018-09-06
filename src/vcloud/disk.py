import vcloud.client as Client

from pyvcloud.vcd.client import TaskStatus
from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.client import VCLOUD_STATUS_MAP
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.utils import extract_id
from vcloud.vapp import find_vm_in_vapp
from vcloud.utils import size_to_bytes, bytes_to_size

find_disk = \
    lambda x, disk: next(([i['id'], i['attached_vm']] for i in x if i['name'] == disk), [None, None])

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
    attached_vm = \
        lambda x, disk: next((i['vm'] for i in x if i['disk'] == disk), None)
    try:
        disks = ctx.vdc.get_disks()
        disks_relation = get_vm_disk_relation(ctx)
        for disk in disks:
            disk_id = extract_id(disk.get('id'))
            result.append(
                {
                    'name': disk.get('name'),
                    'id': disk_id,
                    'href': disk.get('href'),
                    'bus_type': int(disk.get('busType')),
                    'bus_sub_type': disk.get('busSubType'),
                    'size_bytes': int(disk.get('size')),
                    'size_human': bytes_to_size(
                            int(disk.get('size'))
                    ),
                    'status': VCLOUD_STATUS_MAP.get(int(disk.get('status'))),
                    'attached_vm': attached_vm(disks_relation, disk_id),
                    'vdc': extract_id(ctx.vdc.resource.get('id'))
                }

            )
        # Refresh session after Typed Query
        Client.login(session_id=ctx.token)
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return result

def get_vm_disk_relation(ctx):
    result = []
    try:
        resource_type = 'vmDiskRelation'
        query = ctx.client.get_typed_query(
                resource_type,
                query_result_format=QueryResultFormat.ID_RECORDS)
        records = list(query.execute())
        for curr_disk in records:
            result.append(
                {
                    'disk': extract_id(curr_disk.get('disk')),
                    'vdc': extract_id(curr_disk.get('vdc')),
                    'vm': extract_id(curr_disk.get('vm'))
                }
            )
    except Exception as e:
        if ctx.config['debug'] == True:
            raise
        else:
            pass
    return result
