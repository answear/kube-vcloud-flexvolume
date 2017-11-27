kube-vcloud-flexvolume
======================

VMware vCloud Director [flexVolume](https://kubernetes.io/docs/concepts/storage/volumes/#out-of-tree-volume-plugins)
driver for Kubernetes.


Status
======

Highly experimental and under heavy development. Do not use on a system that you care about the data.


Description
============

vcloud-flexvolume provides a storage driver using vCloud's Independent Disk feature. The Independent Disk provides
persistent disk storage which can be attached to instances running in vCloud Director environment.


Installation
============

*  Make sure kubelet is running with `--enable-controller-attach-detach=false`
*  Create the directory `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/sysoperator.pl~vcloud`
*  Install wrapper `scripts/vcloud` as `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/sysoperator.pl~vcloud/vcloud`
*  Create the directory `/opt/vcloud-flexvolume/etc`
*  Install configuration file `config/config.yaml.example` as `/opt/vcloud-flexvolume/etc/config.yaml` and set parameters.

Install packages:

*  python
*  python-pip
*  python-pip-whl
*  python-setuptools
*  python-flufl.enum
*  python-lxml
*  python-netaddr
*  python-progressbar
*  python-pyudev
*  python-pyvmomi

Install the driver itself:

```
python setup.py build
sudo python setup.py install
```

Create a Kubernetes Pod such as:

```
cat examples/nginx.yaml | kubectl apply -f -
```

The driver will create an independent disk with name "testdisk" and size 1Gi under storage profile "T1".
The volume will also be mounted as /data inside the container.


Options
=======

Following options are required:

*  volumeName - Name of the independent disk volume.
*  size - Size to allocate for the new independent disk volume. Accepts any value in human-readable format. (e.g. 100Mi, 1Gi)
*  storage - Name of the storage pool.

Optional options may be passed:

*  mountoptions - Additional options passed to mount. (e.g. noatime, relatime, nobarrier)

TODO
====

*  Write some tests.
*  ~~Functions in flexvolume/mount.py should raise Exceptions just like the ones in attach.py.~~
