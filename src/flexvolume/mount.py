import os
import stat
import subprocess
import json
import click

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

from .cli import cli, error, info, success

@cli.command(short_help='mount the device to a global path')
@click.argument('mountdir')
@click.argument('mountdev')
@click.argument('params')
@click.pass_context
def mountdevice(ctx,
                mountdir,
                mountdev,
                params):
    params = json.loads(params)
    try:
        mode = os.stat(mountdev).st_mode
        assert stat.S_ISBLK(mode) == True
    except (OSError, AssertionError):
        failure = {
            "status": "Failure",
            "message": mountdev + " does not exist"
        }
        error(failure)

    if ismounted(mountdir):
        info(success)

    process = subprocess.Popen(["blkid", "-o", "value", "-s", "TYPE", mountdev], stdout=subprocess.PIPE)
    fstype, err = process.communicate()
    fstype = fstype.strip()
    if fstype == "":
        fstype = params["kubernetes.io/fsType"]
        try:
            subprocess.check_call(["mkfs", "-t", fstype, "-F", mountdev], stdout=DEVNULL, stderr=DEVNULL)
        except CalledProcesError:
            failure = {
                "status": "Failure",
                "message": "Failed to create filesystem " + fstype + " on device " + mountdev
            }
            error(failure)
    try:
        os.stat(mountdir)
    except:
        os.mkdir(mountdir)
    
    try:
        mountopts = params["mountoptions"].split(",")
    except:
        mountopts = []
        
    if mount(mountdev, mountdir, mountopts):
        info(success)

    failure = {
        "status": "Failure",
        "message": "Failed to mount volume at " + mountdir
    }
    error(failure)


@cli.command(short_help='unmount the global mount for the device')
@click.argument('mountdir')
@click.pass_context
def unmountdevice(ctx,
                  mountdir):
    failure = {
        "status": "Failure",
        "message": "Failed to unmount volume at " + mountdir
    }

    if ismounted(mountdir) == False:
        info(success)

    if umount(mountdir) == False:
        error(failure)

    info(success)

def ismounted(mountdir):
    try:
        assert os.path.ismount(mountdir) == True
        return True
    except AssertionError:
        return False

def mount(mountdev, mountdir, mountopts=[]):
    params = ["mount", mountdev, mountdir]
    if len(mountopts) > 0:
        mountopts = [",".join(mountopts)]
        mountopts.insert(0, "-o")

    index = 1
    for elem in mountopts:
        params.insert(index, elem)
        index += 1

    try:
        return subprocess.check_call(params, stderr=DEVNULL)
    except CalledProcessError:
        return False

def umount(mountdir):
    try:
        return subprocess.check_call(["umount", mountdir], stderr=DEVNULL)
    except CalledProcessError:
        return False