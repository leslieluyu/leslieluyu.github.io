#!/bin/bash

# Check if a log file path was provided as a command line argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <log_file>"
    exit 1
fi

# Get the log file path from the command line argument
log_file="$1"


# Initialize variables
cpu=""
duration=""
prompt=""
completion=""
latency=""

# Read the log file line by line
while IFS= read -r line; do
    # Extract information from each line
    if [[ $line == *"CPU_Value="* ]]; then
        cpu=$(echo "$line" | grep -oP 'CPU_Value=\K\d+')
    elif [[ $line == *"Total Duration:"* ]]; then
        duration=$(echo "$line" | grep -oP 'Total Duration:\s+\K\d+\.\d+')
    elif [[ $line == *"Prompt Tokens:"* ]]; then
        prompt=$(echo "$line" | grep -oP 'Prompt Tokens:\s+\K\d+')
    elif [[ $line == *"Completion Tokens:"* ]]; then
        completion=$(echo "$line" | grep -oP 'Completion Tokens:\s+\K\d+')
    elif [[ $line == *"Latency per Token:"* ]]; then
        latency=$(echo "$line" | grep -oP 'Latency per Token:\s+\K\d+\.\d+')
    fi

    # Check if all values are present
    if [[ -n "$cpu" && -n "$duration" && -n "$prompt" && -n "$completion" && -n "$latency" ]]; then
        # Print the formatted line
        echo "CPU_Value:$cpu, $duration, $prompt, $completion, $latency"
        
        # Reset variables for the next line
        cpu=""
        duration=""
        prompt=""
        completion=""
        latency=""
    fi
done < "$log_file"
