#!/bin/bash

# Check if a log file path was provided as a command line argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <log_file>"
    exit 1
fi

# Get the log file path from the command line argument
log_file="$1"

# Check if the log file exists
if [ ! -f "$log_file" ]; then
    echo "Error: Log file '$log_file' not found."
    exit 1
fi

# Filter out valid data rows based on the timestamp format
#valid_data=$(grep -E '^[0-9]{2}:[0-9]{2}:[0-9]{2}' "$log_file")
valid_data=$(grep -E '^[0-9]{2}:[0-9]{2}:[0-9]{2}' ${log_file} | tail -n +2 | head -n -3)
#echo "valid_data="
#echo ${valid_data}

# Calculate the new average and store it in a variable
average=$(echo "$valid_data" | awk 'BEGIN {
    sum_usr = 0;
    sum_system = 0;
    sum_wait = 0;
    sum_CPU = 0;
    count = 0;
}
{
    sum_usr += $4;
    sum_system += $5;
    sum_wait += $7;
    sum_CPU += $8;
    count++;
} END {
    if (count > 0) {
        printf "Average:\t0\t0\t%.2f\t%.2f\t0\t%.2f\t%.2f\t-\n", sum_usr/count, sum_system/count, sum_wait/count, sum_CPU/count
    }
}')
# Replace the original log file with the updated average
echo -e "$log_file \t$average" #>> "$log_file"

# Display the new log file with the updated average
#cat "$log_file"

