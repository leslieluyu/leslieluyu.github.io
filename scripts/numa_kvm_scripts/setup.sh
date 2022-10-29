#!/bin/bash

#CURRENT_USER=ubuntu

sudo apt-get install -y qemu-system-x86 qemu-kvm qemu libvirt-dev libvirt-clients virt-manager virtinst bridge-utils cpu-checker virt-viewer cloud-image-utils
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER

wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img
sudo mkdir /var/lib/libvirt/images/base
sudo mv focal-server-cloudimg-amd64.img /var/lib/libvirt/images/base/ubuntu-20.04.qcow2

#ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="intel_iommu=on"/' /etc/default/grub
sudo update-grub
