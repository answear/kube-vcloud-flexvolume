Kubernetes external vcloud-flexvolume provisioner
=================================================

This is external provisioner for VMware vCloud Director [flexVolume driver](../../) for Kubernetes.


Compilation
===========

```
mkdir $HOME/gopath
export GOPATH=$HOME/gopath
git clone git@github.com:answear/kube-vcloud-flexvolume.git
cd kube-vcloud-flexvolume/provisioner
go get -d ./...
make compile
```


Installation
============

*  Deploy provisioner to Kubernetes:

```
cd kube-vcloud-flexvolume/provisioner
kubectl apply -f deployment/rbac.yaml -f deployment/deployment.yaml
```

*  Customize [deployment/storageclass.yaml](deployment/storageclass.yaml) to suit your needs and deploy:

```
kubectl apply -f deployment/storageclass.yaml
```


Releasing your Docker image
===========================

```
cd kube-vcloud-flexvolume/provisioner
make REGISTRY=YOUR_REGISTRY VERSION=YOUR_VERSION
```


TODO
====

*  Volume deletion is implemented partially (only some safety checks). For full implementation `vcloud-flexvolume delete` command should be invoked using `os/exec.Command()`.

