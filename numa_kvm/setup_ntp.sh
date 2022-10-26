#!/bin/bash


# check if already set
timedatectl | grep -q "synchronized: yes" && exit 0


NTPCONF_FILE="/etc/systemd/timesyncd.conf"
sudo sed -i "s/^#\?NTP=/NTP=corp.intel.com/g" $NTPCONF_FILE
sudo systemctl restart systemd-timesyncd.service
timedatectl
