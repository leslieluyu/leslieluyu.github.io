#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -b <begin_index> -e <end_index> -l <label>"
    exit 1
}

# Parse command-line arguments
while getopts ":b:e:l:" opt; do
    case ${opt} in
        b )
            BEGIN_INDEX=$OPTARG
            ;;
        e )
            END_INDEX=$OPTARG
            ;;
        l )
            LABEL=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if all required arguments are provided
if [ -z "$BEGIN_INDEX" ] || [ -z "$END_INDEX" ] || [ -z "$LABEL" ]; then
    usage
fi

# Define the node name prefix
NODE_NAME_PREFIX="opea-temp-16node-"

# Loop to apply the label
for ((i=BEGIN_INDEX; i<=END_INDEX; i++))
do
    NODE_NAME="${NODE_NAME_PREFIX}${i}"
    kubectl label --overwrite nodes "$NODE_NAME" "$LABEL"
    echo "Applied label $LABEL to node $NODE_NAME"
done
