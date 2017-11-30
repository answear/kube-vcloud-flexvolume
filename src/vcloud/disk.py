from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.client import VCLOUD_STATUS_MAP
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
        disk_resource = ctx.vca.add_disk(
                ctx.config['vdc'],
                name,
                size=size,
                storage_profile_name=storage_profile_name,
                bus_type=bus_type,
                bus_sub_type=bus_sub_type
        )
        tasks = disk_resource[1].get_Tasks()

        if tasks:
            disk_id = disk_resource[1].get_id()
            assert ctx.vca.block_until_completed(tasks[0]) == True
    except Exception as e:
        return ""
    return disk_id

def delete_disk(ctx, name):
    result = []
    try:
        disks = get_disks(ctx)
        for disk in disks:
            if disk['name'] == name:
                ctx.vca.delete_disk(
                        ctx.config['vdc'],
                        name,
                        disk['id']
                )
                result.append(disk['id'])
    except Exception as e:
        pass
    return result

def attach_disk(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    task = vapp.attach_disk_to_vm(vm['vm_name'], disk_ref)

                    if task:
                        return True
    except Exception as e:
        pass
    return False

def attach_disk_t(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    task = vapp.attach_disk_to_vm(vm['vm_name'], disk_ref)

                    if task:
                        return task
    except Exception as e:
        pass
    return False

def attach_disk_b(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    task = vapp.attach_disk_to_vm(vm['vm_name'], disk_ref)

                    if task:
                        assert ctx.vca.block_until_completed(task) == True
                    return True
    except Exception as e:
        pass
    return False

def detach_disk(ctx, vm_name, disk_name):
    try:
        vdc = ctx.vca.get_vdc(ctx.config['vdc'])
        vm = find_vm_in_vapp(ctx, vm_name)
        if len(vm) > 0:
            vm = vm[0]
            vapp = ctx.vca.get_vapp(
                    vdc,
                    vm['vapp_name']
            )
            disk_refs = ctx.vca.get_diskRefs(vdc)
            for disk_ref in disk_refs:
                if disk_ref.name == disk_name:
                    vapp.detach_disk_from_vm(vm['vm_name'], disk_ref)
                    return True
    except Exception as e:
        pass
    return False

def get_disks(ctx):
    result = []
    attached_vm = \
        lambda x, disk: next((i['vm'] for i in x if i['disk'] == disk), None)
    try:
        resource_type = 'disk'
        query = ctx.client.get_typed_query(
                resource_type,
                query_result_format=QueryResultFormat.ID_RECORDS)
        disks = list(query.execute())
        disks_relation = get_vm_disk_relation(ctx)
        for disk in disks:
            if disk.get('vdcName') != ctx.config['vdc']:
                continue
            disk_id = extract_id(disk.get('id'))
            result.append(
                {
                    'name': disk.get('name'),
                    'id': disk_id,
                    'bus_type': int(disk.get('busType')),
                    'bus_sub_type': disk.get('busSubType'),
                    'size_bytes': int(disk.get('sizeB')),
                    'size_human': bytes_to_size(
                            int(disk.get('sizeB'))
                    ),
                    'status': disk.get('status'),
                    'attached_vm': attached_vm(disks_relation, disk_id),
                    'vdc': extract_id(disk.get('vdc'))
                }

            )
    except Exception as e:
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
        pass
    return result
