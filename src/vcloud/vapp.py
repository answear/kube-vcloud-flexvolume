from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.client import VCLOUD_STATUS_MAP
from pyvcloud.vcd.utils import extract_id

def find_vm_in_vapp(ctx, vm_name=None, vm_id=None):
    result = []
    try:
        resource_type = 'vApp'
        query = ctx.client.get_typed_query(
                resource_type,
                query_result_format=QueryResultFormat.ID_RECORDS)
        records = list(query.execute())
        for curr_vapp in records:
            vapp_id = curr_vapp.get('id')
            vapp_name = curr_vapp.get('name')
            the_vapp = ctx.vdc.get_vapp(vapp_name)
            for vm in the_vapp.Children.Vm:
                if vm.get('name') == vm_name or \
                        extract_id(vm.get('id')) == vm_id:
                    result.append(
                        {
                            'vapp': extract_id(vapp_id),
                            'vapp_name': vapp_name,
                            'vm': extract_id(vm.get('id')),
                            'vm_name': vm.get('name'),
                            'status': VCLOUD_STATUS_MAP.get(int(vm.get('status')))
                        }
                    )
                    break
    except Exception as e:
        pass
    return result
