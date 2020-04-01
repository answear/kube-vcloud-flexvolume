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

package main

import (
	"flag"
	"strings"

	"github.com/golang/glog"
	vol "github.com/answear/kube-vcloud-flexvolume/provisioner/pkg/volume"
	"sigs.k8s.io/sig-storage-lib-external-provisioner/controller"
	"k8s.io/apimachinery/pkg/util/validation"
	"k8s.io/apimachinery/pkg/util/validation/field"
	"k8s.io/apimachinery/pkg/util/wait"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

var (
	provisionerName = flag.String("provisionerName", "provisioner.answear.com/vci",
			"Name of the provisioner. The provisioner will only provision volumes for claims that request a StorageClass with a provisioner field set equal to this name.")
	flexDriver      = flag.String("flexDriver",      "answear.com/vcloud",
			"The flexVolume driver.")
	master          = flag.String("master",          "",
			"Master URL to build a client config from. Either this or kubeconfig needs to be set if the provisioner is being run out of cluster.")
	kubeconfig      = flag.String("kubeconfig",      "",
			"Absolute path to the kubeconfig file. Either this or master needs to be set if the provisioner is being run out of cluster.")
)

func main() {
	flag.Set("logtostderr", "true")
	flag.Parse()

	if errs := validateProvisioner(*provisionerName, field.NewPath("provisionerName")); len(errs) != 0 {
		glog.Fatalf("Invalid provisioner specified: %v", errs)
	}
	glog.Infof("Provisioner %s specified", *provisionerName)

	if flexDriver == nil || *flexDriver == "" {
		glog.Fatalf("Invalid flags specified: must provide flexVolume driver")
	}

	// Create the client according to whether we are running in or out-of-cluster
	var config *rest.Config
	var err error
	if *master != "" || *kubeconfig != "" {
		glog.Infof("Either master or kubeconfig specified. building kube config from that..")
		config, err = clientcmd.BuildConfigFromFlags(*master, *kubeconfig)
	} else {
		glog.Infof("Building Kube configs for running in cluster...")
		config, err = rest.InClusterConfig()
	}
	if err != nil {
		glog.Fatalf("Failed to create config: %v", err)
	}
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		glog.Fatalf("Failed to create client: %v", err)
	}

	// The controller needs to know what the server version is because out-of-tree
	// provisioners aren't officially supported until 1.5
	serverVersion, err := clientset.Discovery().ServerVersion()
	if err != nil {
		glog.Fatalf("Error getting server version: %v", err)
	}

	// Create the provisioner: it implements the Provisioner interface expected by
	// the controller
	vciProvisioner := vol.NewVCIProvisioner(*provisionerName, *flexDriver)

	// Start the provision controller which will dynamically provision VCI PVs
	pc := controller.NewProvisionController(clientset, *provisionerName, vciProvisioner, serverVersion.GitVersion)
	pc.Run(wait.NeverStop)
}

// validateProvisioner tests if provisioner is a valid qualified name.
// https://github.com/kubernetes/kubernetes/blob/release-1.4/pkg/apis/storage/validation/validation.go
func validateProvisioner(provisioner string, fldPath *field.Path) field.ErrorList {
	allErrs := field.ErrorList{}
	if len(provisioner) == 0 {
		allErrs = append(allErrs, field.Required(fldPath, provisioner))
	}
	if len(provisioner) > 0 {
		for _, msg := range validation.IsQualifiedName(strings.ToLower(provisioner)) {
			allErrs = append(allErrs, field.Invalid(fldPath, provisioner, msg))
		}
	}
	return allErrs
}
