#!/bin/bash

#####################################################
##For ubuntu 22.04, intel proxy, and ice NIC driver

######################################################
#######Change these fieleds for each nodes###########
IP1=172.31.150.15/24
IP2=172.31.151.15/24
INSTANCE1_NAME=worker3-numa0
INSTANCE2_NAME=worker3-numa1

#######################################################
###Change this feileds for each HW configuration#######
# make sure ETH1 is the device name with IP1 
# and ETH2 is the device name with IP2
ETH1=ens2
ETH2=enp187s0

# default gateway ip address
GATEWAY1=172.31.150.16
GATEWAY2=172.31.151.16

IMAGE_SIZE=30G
VCPU_CFG="sockets=1,cores=56,threads=2"
CPU_SET1="0-55,112-167"
CPU_SET2="56-111,168-223"
MEM_SIZE=393216 #384G
VM_ETH2=enp5s0
SSH_PUB_FILE=~/.ssh/id_rsa.pub
HTTP_PROXY=http://proxy-dmz.intel.com:912
NO_PROXY=localhost,127.0.0.1,intel.com,.intel.com,172.31.150.0/24,172.31.151.0/24,192.168.0.0/16,172.16.27.0/24

function get_pci_from_eth() {
  ETHNAME=$1
  PCI_ID=$(ethtool -i $ETHNAME | grep bus-info | awk '{print $2}' | sed -r 's/[:.]+/_/g')
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
write_files:
  - path: /etc/apt/apt.conf.d/00-proxy
    permissions: 0640
    owner: root
    content: |
      Acquire::http { Proxy "$HTTP_PROXY"; };
      Acquire::https { Proxy "$HTTP_PROXY"; };
      Acquire::http::Pipeline-Depth "23";
      Acquire::Languages "none";
packages:
 - linux-firmware
 - linux-modules-extra-5.15.0-52-generic
runcmd:
 - modprobe ice
 - echo "export http_proxy=$HTTP_PROXY" >>/etc/environment
 - echo "export https_proxy=$HTTP_PROXY" >>/etc/environment
 - echo "export no_proxy=$NO_PROXY" >>/etc/environment

# written to /var/log/cloud-init-output.log
final_message: "The system is finally up, after $UPTIME seconds"
EOF
cat >network.cfg.$INAME <<EOF
version: 2
ethernets:
  enp1s0:
     dhcp4: true
  ${VM_ETH2}:
     addresses: [ $IP ]
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
--ram $MEM_SIZE --vcpus=$VCPU_CFG  --os-type linux --os-variant ubuntu22.04 \
--disk path=/var/lib/libvirt/images/$NAME/$NAME.qcow2,format=qcow2 \
--disk /var/lib/libvirt/images/$NAME/user-data.img,device=cdrom \
--import --noautoconsole \
--host-device=$PCI \
--cpu host-passthrough,cache.mode=passthrough \
--cpuset=$CPUSET --numatune $NUMANODE
}

## clean environment
VMS=$(virsh list --all | awk 'NR > 2 { print $2}')
for vm in $VMS;
do
    virsh destroy $vm
    virsh undefine $vm
done

ip link|grep -w $ETH1
if [ $? -ne 0 ]; then
  echo "Ethernet $ETH1 detect failed"
  #exit -1
fi

ip link|grep -w $ETH2
if [ $? -ne 0 ]; then
  echo "Ethernet $ETH2 detect failed"
  #exit -1
fi
## prepare for instance-1
PCI_DEVICE1=$(get_pci_from_eth $ETH1)
prepare_instance $INSTANCE1_NAME ${PCI_DEVICE1} ${CPU_SET1} 0 $IP1 $GATEWAY1

## prepare for instance-2
PCI_DEVICE2=$(get_pci_from_eth $ETH2)
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
