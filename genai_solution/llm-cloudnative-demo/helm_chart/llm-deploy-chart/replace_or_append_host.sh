#!/bin/bash

# Function to replace or add a host in /etc/hosts
replace_or_add_host() {
    host_ip="$1"
    host_name="$2"

    # Check if the host already exists in /etc/hosts
    if grep -q "$host_name" /etc/hosts; then
        sudo sed -i "/$host_name/c\\$host_ip\t$host_name" /etc/hosts
        echo "Host '$host_name' updated with IP '$host_ip' in /etc/hosts"
    else
        echo -e "$host_ip\t$host_name" | sudo tee -a /etc/hosts > /dev/null
        echo "Host '$host_name' added with IP '$host_ip' to /etc/hosts"
    fi
}

replace_or_add_host $1 $2