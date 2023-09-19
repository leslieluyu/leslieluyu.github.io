#!/bin/bash

# Define NUMA node CPU information
NUMA_NODE0_CPUS="0-23,48-71"
NUMA_NODE1_CPUS="24-47,72-95"

# Define max_cpu and step values
max_cpu=${1:-96}
step=${2:-8}
i00=$((max_cpu/4))
i01=$((2*max_cpu/4))
i10=$((3*max_cpu/4))
i11=$((max_cpu-4))
n00=$((max_cpu/4-1))
n01=$((3*max_cpu/4-1))
n10=$((2*max_cpu/4-1))
n11=$((max_cpu-1))
echo "$n00,$n01,$n10,$n11"
#exit 0

# Initialize variables
current_cpu=0
numa_command=""

# Loop until current_cpu reaches max_cpu
while [ "$current_cpu" -lt "$max_cpu" ]; do
  # Increment current_cpu by step
  current_cpu=$((current_cpu+step))
  # Print the numactl command
  echo "$numa_command"
  if [ "$current_cpu" -eq 0 ]; then
    # Handle the initial case separately
    numa_command="numactl 0-$((step-1))"
  else
    if [ "$current_cpu" -lt "$i00" ]; then
      numa_command="numactl 0-$current_cpu"
      continue
    fi    
    if [ "$current_cpu" -lt "$i01" ]; then
      numa_command="numactl 0-$n00,$i01-$((current_cpu+i00))"
      continue
    fi
    if [ "$current_cpu" -lt "$i10" ]; then
      numa_command="numactl 0-$n00,$i01-$n01,$i00-$((current_cpu-i00))"
      continue
    fi
    if [ "$current_cpu" -le "$i11" ]; then
      numa_command="numactl 0-$n00,$i01-$n01,$i00-$n10,$i10-$current_cpu"
      continue
    else
      break
    fi
    echo "Failed! current_cpu=$current_cpu,n00=$n00"
  fi

  # Print the numactl command
  echo "$numa_command"

  # Increment current_cpu by step
  current_cpu=$((current_cpu+step))
done

