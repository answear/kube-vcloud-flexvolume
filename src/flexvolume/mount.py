import os
import stat
import subprocess
import json
import click
import sys

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

from .cli import cli, error, info, GENERIC_SUCCESS, GENERIC_NOTSUPPORTED

@cli.command(short_help='mount the volume at the mount dir')
@click.argument('mountdir')
@click.argument('params')
@click.pass_context
def mount(ctx,
          mountdir,
          params):
    params = json.loads(params)
    info(GENERIC_NOTSUPPORTED)

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
        try:
            mode = os.stat(mountdev).st_mode
            assert stat.S_ISBLK(mode) == True
        except (OSError, AssertionError):
            raise Exception(
                    ("Mount device '%s' does not exist") % (mountdev)
            )

        if ismounted(mountdir):
            info(GENERIC_SUCCESS)

        process = subprocess.Popen(['blkid', '-o', 'value', '-s', 'TYPE', mountdev], stdout=subprocess.PIPE)
        fstype, err = process.communicate()
        fstype = fstype.strip()
        if fstype.decode() == "":
            fstype = params['kubernetes.io/fsType']
            try:
                subprocess.check_call(["mkfs", "-t", fstype, mountdev], stdout=DEVNULL, stderr=DEVNULL)
            except subprocess.CalledProcesError:
                raise Exception(
                        ("Failed to create filesystem '%s' on mount device '%s'") % (fstype, mountdev)
                )
        try:
            os.stat(mountdir)
        except:
            os.mkdir(mountdir)

        try:
            mountopts = params['mountoptions'].split(',')
        except:
            mountopts = []

        if mount(mountdev, mountdir, mountopts):
            info(GENERIC_SUCCESS)

        raise Exception(
                ("Failed to mount device '%s' at '%s'") % (mountdev, mountdir)
        )
    except Exception as e:
        failure = {
            "status": "Failure",
            "message": (
                    ("Error on line %d in file %s (%s): %s") % 
                    (sys.exc_info()[-1].tb_lineno, sys.exc_info()[-1].tb_frame.f_code.co_filename, type(e).__name__, e)
            )
        }
        error(failure)

@cli.command(short_help='unmount the volume')
@click.argument('mountdir')
@click.pass_context
def unmount(ctx,
            mountdir):
    info(GENERIC_NOTSUPPORTED)

@cli.command(short_help='unmount the global mount for the device')
@click.argument('mountdir')
@click.pass_context
def unmountdevice(ctx,
                  mountdir):
    failure = {
        "status": "Failure",
        "message": ("Failed to unmount device from '%s'") % (mountdir)
    }

    if ismounted(mountdir) == False:
        info(GENERIC_SUCCESS)

    if umount(mountdir) == False:
        error(failure)

    info(GENERIC_SUCCESS)

def ismounted(mountdir):
    try:
        assert os.path.ismount(mountdir) == True
        return True
    except AssertionError:
        return False

def mount(mountdev, mountdir, mountopts=[]):
    params = ['mount', mountdev, mountdir]
    if len(mountopts) > 0:
        mountopts = [','.join(mountopts)]
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
        subprocess.check_call(['umount', mountdir], stderr=DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
