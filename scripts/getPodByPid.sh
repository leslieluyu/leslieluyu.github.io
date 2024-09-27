#!/bin/bash
PID=$1
CGROUP=$(cat /proc/$PID/cgroup | grep kubepods)
PODID=$(echo $CGROUP | sed -n 's/.*pod\([^/]*\).*/\1/p')
kubectl get pods --all-namespaces -o json | jq -r '.items[] | select(.metadata.uid == "'$PODID'") | .metadata.name + " " + .metadata.namespace'
