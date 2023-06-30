#!/bin/bash

BIN_MAP="/home/ansible/yulu/perf-map-agent/bin/create-java-perf-map.sh"


# Run pgrep to get the PIDs of Java processes
pids=$(pgrep java)

# Check if any Java processes are running
if [[ -z $pids ]]; then
	  echo "No Java processes found."
	    exit 1
fi

# Iterate over the PIDs and create map files
for pid in $pids; do
	  echo "Creating map file for PID: $pid"
	    $BIN_MAP $pid
    done


echo "finish export the symbols of all java process"

