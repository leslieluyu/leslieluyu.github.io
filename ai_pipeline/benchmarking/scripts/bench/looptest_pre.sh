#!/bin/bash

#install some required command
ansible -i hosts emon -m shell -a "sudo apt install -y sysstat linux-tools-`uname -r`"

# Make sure cpu power policy setting to performance
ansible -i hosts emon --become -m shell -a "cpupower frequency-set -g performance > /dev/null"
ansible -i hosts emon --become -m shell -a "cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
