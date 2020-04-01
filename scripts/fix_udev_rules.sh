#!/bin/bash

set -e

pushd /etc/udev/rules.d
# old: SUBSYSTEM=="block", ENV{DEVNAME}=="/dev/sdb", SYMLINK+="block/28a96fc1-dba6-43a9-a814-42d135443d51"
# new: SUBSYSTEM=="block", ENV{ID_TYPE}=="disk", ENV{DEVTYPE}=="disk", ENV{ID_PATH}=="pci-0000:03:00.0-scsi-0:0:1:0", SYMLINK+="block/28a96fc1-dba6-43a9-a814-42d135443d51"
for udev_rule_file in 90-independent-disk* ; do
    udev_rule=$(< $udev_rule_file)
    disk=${udev_rule_file##*-}
    disk=${disk%%.*}
    disk_symlink=$(echo $udev_rule | sed -e 's/.*SYMLINK+="\(.*\)"/\1/')
    disk_urn=${disk_symlink##*/}
    disk_path=$(find -L /dev/disk/by-path -samefile /dev/$disk)
    cat > 90-vcloud-idisk-$disk_urn.rules <<EOF
SUBSYSTEM=="block", ENV{ID_TYPE}=="disk", ENV{DEVTYPE}=="disk", ENV{ID_PATH}=="${disk_path##*/}", SYMLINK+="$disk_symlink"
EOF
    rm -f $udev_rule_file && udevadm control --reload-rules
done
popd
