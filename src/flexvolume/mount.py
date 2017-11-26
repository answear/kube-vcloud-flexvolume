import os
import stat
import subprocess
import json
import click

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

from .cli import cli, error, info, GENERIC_SUCCESS

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
            "message": ("Device '%s' does not exist") % (mountdev)
        }
        error(failure)

    if ismounted(mountdir):
        info(GENERIC_SUCCESS)

    process = subprocess.Popen(["blkid", "-o", "value", "-s", "TYPE", mountdev], stdout=subprocess.PIPE)
    fstype, err = process.communicate()
    fstype = fstype.strip()
    if fstype == "":
        fstype = params["kubernetes.io/fsType"]
        try:
            subprocess.check_call(["mkfs", "-t", fstype, mountdev], stdout=DEVNULL, stderr=DEVNULL)
        except subprocess.CalledProcesError:
            failure = {
                "status": "Failure",
                "message": ("Failed to create filesystem '%s' on device '%s'") % (fstype, mountdev)
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
        info(GENERIC_SUCCESS)

    failure = {
        "status": "Failure",
        "message": ("Failed to mount device '%s' at '%s'") % (mountdev, mountdir)
    }
    error(failure)


@cli.command(short_help='unmount the global mount for the device')
@click.argument('mountdir')
@click.pass_context
def unmountdevice(ctx,
                  mountdir):
    failure = {
        "status": "Failure",
        "message": ("Failed to unmount device '%s' from '%s'") % (mountdev, mountdir)
    }

    if ismounted(mountdir) == False:
        info(GENERIC_SUCCESS)

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
        subprocess.check_call(params, stderr=DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def umount(mountdir):
    try:
        subprocess.check_call(["umount", mountdir], stderr=DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
