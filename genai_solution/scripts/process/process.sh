#!/bin/bash

# Define the input file
input_file="metrics.log"

# Print the header for the output table
echo -e "podName\tcpu_utilization_sum_max\tcpu_utilization_sum_min\tcpu_utilization_sum_average\tMemorybw_sum_max\tMemorybw_sum_min\tMemorybw_sum_average\tMemory_sum_max"

# Initialize variables to hold overall sums
total_cpu_max=0
total_cpu_min=0
total_cpu_sum=0
total_mem_max=0
total_mem_min=0
total_mem_sum=0
pod_count=0

# Read the input file line by line
while IFS= read -r line; do
    # Check if the line contains 'podName'
    if [[ $line == podName* ]]; then
        # Extract podName
        podName=$(echo "$line" | awk '{print $2}')
        
        # Initialize arrays to hold values for CPU and Memory metrics
        cpu_values=()
        mem_values=()
        
        # Read next lines to extract metrics
        read -r cpu_line
        cpu_values+=($(echo "$cpu_line" | grep -oP '(?<=Values: \[)[^]]+'))
        
        read -r mem_line
        mem_values+=($(echo "$mem_line" | grep -oP '(?<=Values: \[)[^]]+'))
        
        # Process CPU values to calculate max, min, and average
        cpu_max=$(printf "%s\n" "${cpu_values[@]}" | sort -n | tail -n 1)
        cpu_min=$(printf "%s\n" "${cpu_values[@]}" | sort -n | head -n 1)
        cpu_avg=$(printf "%s + %s" "${cpu_values[@]}" | bc -l)
        cpu_avg=$(echo "$cpu_avg / ${#cpu_values[@]}" | bc -l)

        # Process Memory values to calculate max, min, and average
        mem_max=$(printf "%s\n" "${mem_values[@]}" | sort -n | tail -n 1)
        mem_min=$(printf "%s\n" "${mem_values[@]}" | sort -n | head -n 1)
        mem_avg=$(printf "%s + %s" "${mem_values[@]}" | bc -l)
        mem_avg=$(echo "$mem_avg / ${#mem_values[@]}" | bc -l)

        # Print the collected metrics in tabular format
        echo -e "${podName}\t${cpu_max}\t${cpu_min}\t${cpu_avg}\t${mem_max}\t${mem_min}\t${mem_avg}"

        # Update overall sums for later calculations
        total_cpu_max=$(echo "$total_cpu_max + $cpu_max" | bc)
        total_cpu_min=$(echo "$total_cpu_min + $cpu_min" | bc)
        total_cpu_sum=$(echo "$total_cpu_sum + $cpu_avg" | bc)

        total_mem_max=$(echo "$total_mem_max + $mem_max" | bc)
        total_mem_min=$(echo "$total_mem_min + $mem_min" | bc)
        total_mem_sum=$(echo "$total_mem_sum + $mem_avg" | bc)

        ((pod_count++))
    fi
done < "$input_file"

# Calculate overall averages across all pods
if [ $pod_count -gt 0 ]; then
    overall_cpu_avg=$(echo "$total_cpu_sum / $pod_count" | bc -l)
    overall_mem_avg=$(echo "$total_mem_sum / $pod_count" | bc -l)

    # Print overall metrics at the end
    echo -e "Overall\t$total_cpu_max\t$total_cpu_min\t$overall_cpu_avg\t$total_mem_max\t$total_mem_min\t$overall_mem_avg"
fi
