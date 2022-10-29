#!/bin/bash
####################################################
####SR-IOV script, not fully verified yet

IP1=172.31.150.189/24
IP2=172.31.151.189/24
INSTANCE1_NAME=master-numa0
INSTANCE2_NAME=master-numa1

# make sure ETH1 is the device name with IP1 
# and ETH2 is the device name with IP2
SR_IOV_PHY=enp134s0f0

# default gateway ip address
GATEWAY1=172.31.150.161
GATEWAY2=172.31.151.161

IMAGE_SIZE=30G
VCPU_NUM=48
CPU_SET1="0-23,48-71"
CPU_SET2="24-47,72-95"
MEM_SIZE=196608 #192G
VM_ETH2=enp4s0
SSH_PUB_FILE=~/.ssh/id_rsa.team.pub

function get_pci_from_eth() {
  VFID=$1
  PCI_ID=$(realpath /sys/class/net/$SR_IOV_PHY/device/virtfn$VFID/|sed -r 's/[:.]/_/g'|xargs basename)
  echo $( virsh nodedev-list | grep $PCI_ID)
}

function prepare_user_disk() {
  local INAME=$1
  local IP=$2
  local GATEWAY=$3
  SSH_PUB_KEY=$(cat $SSH_PUB_FILE)
  cat >user-data.$INAME <<EOF
#cloud-config
manage_etc_hosts: localhost
fqdn: $INAME.local
users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: users, admin, sudo
    home: /home/ubuntu
    shell: /bin/bash
    lock_passwd: false
    ssh-authorized-keys:
      - $SSH_PUB_KEY
ssh_genkeytypes:
  - rsa
  - dsa
# only cert auth via ssh (console access can still login)
ssh_pwauth: False
disable_root: False
chpasswd:
  list: |
     ubuntu:linux
  expire: False
# written to /var/log/cloud-init-output.log
final_message: "The system is finally up, after $UPTIME seconds"
EOF
cat >network.cfg.$INAME <<EOF
version: 2
ethernets:
  ${VM_ETH2}:
     addresses: [ $IP ]
     gateway4: $GATEWAY
     nameservers:
       addresses: [ 8.8.8.8 ]
       search: [ local ]
EOF
  cloud-localds -N network.cfg.$INAME user-data.img user-data.$INAME
  sudo mv user-data.img /var/lib/libvirt/images/$INAME/user-data.img
}

function prepare_instance() {
    local NAME=$1
    local PCI=$2
    local CPUSET=$3
    local NUMANODE=$4
    local IP=$5
    local GATEWAY=$6
    if [ ! -d "/var/lib/libvirt/images/$NAME" ];
    then
        sudo mkdir /var/lib/libvirt/images/$NAME
    fi
    sudo qemu-img create -f qcow2 -F qcow2 -o backing_file=/var/lib/libvirt/images/base/ubuntu-22.04.qcow2 /var/lib/libvirt/images/$NAME/$NAME.qcow2
    prepare_user_disk $NAME $IP $GATEWAY
    sudo qemu-img resize /var/lib/libvirt/images/$NAME/$NAME.qcow2 $IMAGE_SIZE
    virt-install --connect qemu:///system --virt-type kvm --name $NAME \
--ram $MEM_SIZE --vcpus=$VCPU_NUM --os-type linux --os-variant ubuntu22.04 \
--disk path=/var/lib/libvirt/images/$NAME/$NAME.qcow2,format=qcow2 \
--disk /var/lib/libvirt/images/$NAME/user-data.img,device=cdrom \
--import --nonetwork --noautoconsole \
--host-device=$PCI \
--cpuset=$CPUSET --numatune $NUMANODE
}

## clean environment
VMS=$(virsh list --all | awk 'NR > 2 { print $2}')
for vm in $VMS;
do
    virsh destroy $vm
    virsh undefine $vm
done

sudo -E bash -c 'echo 3 >/sys/class/net/$SR_IOV_PHY/device/sriov_numvfs'
## prepare for instance-1
PCI_DEVICE1=$(get_pci_from_eth 1)
prepare_instance $INSTANCE1_NAME ${PCI_DEVICE1} ${CPU_SET1} 0 $IP1 $GATEWAY1

## prepare for instance-2
PCI_DEVICE2=$(get_pci_from_eth 2)
prepare_instance $INSTANCE2_NAME ${PCI_DEVICE2} ${CPU_SET2} 1 $IP2 $GATEWAY2

echo "Wait for 1 minutes for VMs starting..."
sleep 60

#VM1_IP=$(virsh domifaddr $INSTANCE1_NAME | awk 'match($0, /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/) { print substr( $0, RSTART, RLENGTH )}')
#echo "VM $INSTANCE1_NAME is starting at $VM1_IP."
#VM2_IP=$(virsh domifaddr $INSTANCE2_NAME | awk 'match($0, /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/) { print substr( $0, RSTART, RLENGTH )}')
#echo "VM $INSTANCE2_NAME is starting at $VM2_IP."

#ssh -t $VM1_IP "sudo ip link set $VM_ETH2 up; sudo ip -4 addr add $IP1/24 dev $VM_ETH2"
#ssh -t $VM2_IP "sudo ip link set $VM_ETH2 up; sudo ip -4 addr add $IP2/24 dev $VM_ETH2"
echo "Your VMs have been set up."
