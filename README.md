kube-vcloud-flexvolume
======================

VMware vCloud Director [flexVolume](https://kubernetes.io/docs/concepts/storage/volumes/#out-of-tree-volume-plugins)
driver for Kubernetes.


Status
======

Successfully run this driver on production Kubernetes cluster for over half a year without any loss of data.
The current stable version is: [2.5.3](../../releases/tag/2.5.3).

Version 2.4.0 introduces [external vcloud-provisioner](provisioner) for ease provisioning Persistent Volumes.
Provisioner is deployed inside Kubernetes cluster as a Pod controlled by [Deployment](provisioner/deployment).

WARNING: Versions prior to [2.2.1rc1](../../releases/tag/2.2.1rc1) have a problem with unstable disk paths which under some circumstances could cause data loss.
After upgrade from affected versions make sure udev rules have been properly converted to the new format using [this script](scripts/fix_udev_rules.sh).


Caveats
=======

*  Due to how vCloud works if you want to simultaneously attach/detach disks to/from same VM you should implement a global lock inside attach/detach commands. ~~Check [feature/etcd](../../tree/feature/etcd) branch for experimental implementation using etcd key-value store.~~ (Merged via pull request [#5](../../pr/5))

*  When Kubernetes node is marked unschedulable (with `kubectl drain`) `operationExecutor` on a new node calls `AttachVolume` before `DetachVolume` is called on the old one. We periodically poll the volume to find out if is still attached, but vCloud deletes relation before asynchronous detach:disk task was finished. This sometimes can result in throwing an exception "Could not attach volume '%s' to node '%s'" and repeating the attemp by Kubelet process.

*  Using busType:busSubType combination other than SCSI:VirtualSCSI can lead to unexpected behavior. For example you can attach more than one disk of default type (SCSI:lsilogic), but only the first one will be detected by Linux kernel.

*  When something goes wrong during disk attaching and the driver throws an exception the udev rules required for restoring symlinks after reboot might not be generated. This can result in similar behaviour to one described in [this](../../issues/7) issue. The code tries to minimize the chances of this happening. If the problem occurs, please fill the bug report.


Description
===========

vcloud-flexvolume provides a storage driver using vCloud's Independent Disk feature. The Independent Disk provides
persistent disk storage which can be attached to instances running in vCloud Director environment.

You can read more about Independent Disks [here](https://pubs.vmware.com/vcd-80/index.jsp?topic=/com.vmware.vcloud.api.sp.doc_90/GUID-ED825075-4278-486A-A1EB-FB47FE0226DA.html).


Installation
============

*  Make sure kubelet is running with `--enable-controller-attach-detach=false`
*  Create the directory `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/answear.com~vcloud`
*  Install wrapper `scripts/vcloud` as `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/answear.com~vcloud/vcloud`
*  Create the directory `/opt/vcloud-flexvolume/etc`
*  Install configuration file `config/config.yaml.example` as `/opt/vcloud-flexvolume/etc/config.yaml` and set parameters.

Install packages:

*  python3
*  python3-pip
*  python3-setuptools
*  python3-wheel
*  python3-flufl.enum
*  python3-lxml
*  python3-yaml
*  python3-pygments
*  python3-pyudev

Install the driver itself:

```
git checkout 2.5.3
python3 setup.py build
sudo python3 setup.py install
```

or

```
pip3 install --process-dependency-links git+https://github.com/answear/kube-vcloud-flexvolume.git@2.5.3
```

*  Restart kubelet process.

Create a Kubernetes Pod such as:

```
cat examples/nginx.yaml | kubectl apply -f -
```

The driver will create an independent disk with name "testdisk" and size 1Gi under storage profile "T1".
The volume will also be mounted as /data inside the container.


Upgrading
=========

*  Install the newest driver version using git or pip.
*  Apply any changes in example [config file](config/config.yaml.example) to your local copy.


Options
=======

Following options are required:

*  volumeName - Name of the independent disk volume.
*  size - Size to allocate for the new independent disk volume. Accepts any value in human-readable format. (e.g. 100Mi, 1Gi)

Optional options may be passed:

*  busType - Disk bus type expressed as a string. One of: 5 - IDE, 6 - SCSI (default), 20 - SATA.
*  busSubType - Disk bus subtype expressed as a string. One of: "" (busType=5), buslogic (busType=6), lsilogic (busType=6), lsilogicsas (busType=6), VirtualSCSI (busType=6), vmware.sata.ahci (busType=20).
*  storage - Name of the storage pool.
*  mountOptions - Additional comma-separated options passed to mount. (e.g. noatime, relatime, nobarrier)


Driver invocation
=================

NOTE: Versions prior to 2.4.0 have "mountoptions" (lowercase). For backwards compatibility and for using StorageClass.MountOptions in provisioner we accept both versions.

*  Init:

```
>>> vcloud-flexvolume init
<<< {"status": "Success", "capabilities": {"attach": true}}
```

*  Volume is attached:

```
>>> vcloud-flexvolume isattached '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountOptions":"relatime,nobarrier","size":"1Gi","storage":"T1","busType":6,"busSubType":"VirtualSCSI","volumeName":"testdisk"}' nodename
<<< {"status": "Success", "attached": false}
```

*  Attach:

```
>>> vcloud-flexvolume attach '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountOptions":"relatime,nobarrier","size":"1Gi","storage":"T1","busType":6,"busSubType":"VirtualSCSI","volumeName":"testdisk"}' nodename
<<< {"status": "Success", "device": "/dev/disk/by-path/pci-0000:03:00.0-scsi-0:0:1:0-part1"}
```

The driver detects (using udev events) the name of the device under which it was registered by the Linux kernel and automatically creates symlink `/dev/block/<URN>` pointing to `../<device>`.
URN is a unique volume ID generated by vCloud Director.

*  Wait for attach:

```
>>> vcloud-flexvolume waitforattach /dev/disk/by-path/pci-0000:03:00.0-scsi-0:0:1:0-part1 '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountOptions":"relatime,nobarrier","size":"1Gi","storage":"T1","busType":6,"busSubType":"VirtualSCSI","volumeName":"testdisk"}'
<<< {"status": "Success", "device": "/dev/disk/by-path/pci-0000:03:00.0-scsi-0:0:1:0-part1"}
```

*  Mount device:

```
>>> vcloud-flexvolume mountdevice /mnt/testdisk /dev/disk/by-path/pci-0000:03:00.0-scsi-0:0:1:0-part1 '{"kubernetes.io/fsType":"ext4","kubernetes.io/pvOrVolumeName":"testdisk","kubernetes.io/readwrite":"rw","mountOptions":"relatime,nobarrier","size":"1Gi","storage":"T1","busType":6,"busSubType":"VirtualSCSI","volumeName":"testdisk"}'
<<< {"status": "Success"}
```

*  Unmount device:

```
>>> vcloud-flexvolume unmountdevice /mnt/testdisk
<<< {"status": "Success"}
```

*  Detach:

```
>>> vcloud-flexvolume detach testdisk nodename
<<< {"status": "Success"}
```


TODO
====

*  Write some tests.
*  ~~Functions in flexvolume/mount.py should raise Exceptions just like the ones in attach.py.~~
*  Reuse vCloud API session token between invocations.
*  Validate input JSON with JSON Schema.


Credits
=======

 * [elFarto](https://github.com/elFarto) - for forking and improvements in `Disk.find_disk` and `Disk.get_disks` methods
