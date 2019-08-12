/*
Copyright 2019 Piotr Mazurkiewicz <piotr.mazurkiewicz@wearco.pl>.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package volume

import (
	"sigs.k8s.io/sig-storage-lib-external-provisioner/controller"
	"k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type vciProvisioner struct {
	name       string
	flexDriver string
}

// NewVCIProvisioner creates a new VCI provisioner
func NewVCIProvisioner(name string, flexDriver string) controller.Provisioner {
	provisioner := &vciProvisioner{
		name:       name,
		flexDriver: flexDriver,
	}
	return provisioner
}

var _ controller.Provisioner = &vciProvisioner{}

// Provision creates a storage asset and returns a PV object representing it.
func (p *vciProvisioner) Provision(options controller.ProvisionOptions) (*v1.PersistentVolume, error) {
	annotations := map[string]string{
		"pv.kubernetes.io/provisioned-by": p.name,
	}
	capacity := options.PVC.Spec.Resources.Requests[v1.ResourceName(v1.ResourceStorage)]

	defaults := make(map[string]string)
	defaults["storage"] = "T1"
	defaults["busType"] = "6"
	defaults["busSubType"] = "VirtualSCSI"
	defaults["mountoptions"] = "relatime,nobarrier"

	parameters := options.StorageClass.Parameters

	// Defaults fsType to ext4
	fsType, exists := parameters["fsType"]
	if !exists || fsType == "" {
		fsType = "ext4"
	}
	// Set defaults[k] to options.StorageClass.Parameters[k] if exists
	for k, _ := range defaults {
		opt, exists := parameters[k]
		if exists && opt != "" {
			defaults[k] = opt
		}
	}
	defaults["size"] = capacity.String()
	defaults["volumeName"] = options.PVName

	pv := &v1.PersistentVolume{
		ObjectMeta: metav1.ObjectMeta{
			Name: options.PVName,
			Annotations: annotations,
		},
		Spec: v1.PersistentVolumeSpec{

			PersistentVolumeReclaimPolicy: *options.StorageClass.ReclaimPolicy,
			AccessModes: options.PVC.Spec.AccessModes,
			Capacity: v1.ResourceList{
				v1.ResourceName(v1.ResourceStorage): options.PVC.Spec.Resources.Requests[v1.ResourceName(v1.ResourceStorage)],
			},
			PersistentVolumeSource: v1.PersistentVolumeSource{

				FlexVolume: &v1.FlexPersistentVolumeSource{
					Driver:   p.flexDriver,
					Options:  defaults,
					ReadOnly: false,
					FSType:   fsType,
				},
			},
		},
	}

	return pv, nil
}

// Delete removes the storage asset that was created by Provision represented
// by the given PV.
func (p *vciProvisioner) Delete(volume *v1.PersistentVolume) error {
	return nil
}
