#!/bin/bash

# Set the maximum number (default is 100 if not provided)
max_num=${1:-100}
# Set the path (default is current directory if not provided)
path=${2:-.}

total_size=0

for i in $(seq 1 "$max_num"); do
    # Format the index as a four-digit number without leading zero issues
    formatted_index=$(printf "%04d" "$i")
    filename="${path}/pubmed23n${formatted_index}.txt"
    
    if [ -f "$filename" ]; then  # Check if the file exists
        size=$(stat -c%s "$filename")
        total_size=$((total_size + size))
        echo "$filename size: $size bytes"  # Optional: Print each file's size
    else
        echo "$filename does not exist."
    fi
done

echo "Total Size: $total_size bytes"
