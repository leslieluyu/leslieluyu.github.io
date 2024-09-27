bash
#!/bin/bash

PID=$1

# Get cgroup info and extract the container ID (last part after colon)
CONTAINER_ID=$(cat /proc/$PID/cgroup | grep kubepods | sed -n 's/.*:\(.*\)$/\1/p' | tail -1)

if [ -n "$CONTAINER_ID" ]; then
    # Use crictl to get pod information
    POD_ID=$(crictl ps -a --id $CONTAINER_ID --format json | jq -r '.containers[0].podSandboxId')
    
    if [ -n "$POD_ID" ]; then
        POD_INFO=$(crictl pods --id $POD_ID --format json | jq -r '.pods[0] | .metadata.name + " " + .metadata.namespace')
        echo "Pod Name and Namespace: $POD_INFO"
    else
        echo "Could not find pod ID for container $CONTAINER_ID"
    fi
else
    echo "Could not extract container ID from cgroup information"
fi
