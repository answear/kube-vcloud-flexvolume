import re
import bitmath
import math
import pyudev

from functools import partial 
from glob import glob
from os.path import basename, dirname

def disk_partitions(disk):
    partitions = "/sys/block/%s/*/start" % (disk)
    return [basename(dirname(p)) for p in glob(partitions)]

def size_to_bytes(human_size):
    PARSE_REGEXP = r"(\d+)([MGTPE]i)"
    parse = re.compile(PARSE_REGEXP)
    try:
        size, unit = re.match(parse, human_size).group(1, 2)
        size = int(size)
        assert size > 0

        if unit == 'Mi':
            return int(bitmath.MiB(size).to_Byte())
        elif unit == 'Gi':
            return int(bitmath.GiB(size).to_Byte())
        elif unit == 'Ti':
            return int(bitmath.TiB(size).to_Byte())
        elif unit == 'Pi':
            return int(bitmath.PiB(size).to_Byte())
        elif unit == 'Ei':
            return int(bitmath.EiB(size).to_Byte())
        else:
            return 0
    except Exception as e:
        return 0

def bytes_to_size(size):
    units = ("B", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei") 
    if size == 0:
        return "%d%s" % (size, units[0])

    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%d%s" % (s, units[i])

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
