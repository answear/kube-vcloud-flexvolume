# Copyright 2019 Piotr Mazurkiewicz <piotr.mazurkiewicz@wearco.pl>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ifeq ($(REGISTRY),)
	REGISTRY = gcr.io/wearco
endif
ifeq ($(VERSION),)
	VERSION = latest
endif
IMAGE = $(REGISTRY)/kube-vci-provisioner:$(VERSION)



all: | compile release

compile: | clean
	CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o build/vci-provisioner ./cmd/vci
	strip -g build/vci-provisioner
.PHONY: compile

docker-build:
	docker build -t $(IMAGE) .
.PHONY: docker-build

docker-push:
	docker push $(IMAGE)
.PHONY: docker-push

release: | docker-build docker-push
.PHONY: release

clean:
	rm -f build/vci-provisioner
.PHONY: clean
