labelv09="chatqna=v09"
labelnorerank="chatqna=v09norerank"
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}
#kubectl label --overwrite nodes opea-temp-16node-0 ${labelv09}

#!/bin/bash

# Define the node name prefix and the label variable
NODE_NAME_PREFIX="opea-temp-16node-"
LABEL="${labelv09}"  # Ensure that this variable is set before running the script

# Number of times to apply the label
ITERATIONS=8

# Loop to apply the label
for ((i=0; i<ITERATIONS; i++))
do
    NODE_NAME="${NODE_NAME_PREFIX}${i}"
    #kubectl label --overwrite nodes "$NODE_NAME" "$LABEL"
    echo "Applied label $LABEL to node $NODE_NAME"
done
