#!/bin/bash

MLC="./mlc"   # Path to your mlc executable

# Step 1: Get NUMA info
NUMA_NODES_RANGE=$(cat /sys/devices/system/node/online)
NUMA_NODES=()
if [[ "$NUMA_NODES_RANGE" =~ "-" ]]; then
    start=${NUMA_NODES_RANGE%-*}
    end=${NUMA_NODES_RANGE#*-}
    for ((i=start; i<=end; i++)); do
        NUMA_NODES+=($i)
    done
else
    NUMA_NODES=($NUMA_NODES_RANGE)
fi

# Step 2: Select CPU cores (one per NUMA node)
get_first_cpu() {
    local node=$1
    local cpulist=$(cat /sys/devices/system/node/node${node}/cpulist)
    local IFS=,
    read -ra parts <<< "$cpulist"
    for part in "${parts[@]}"; do
        if [[ "$part" =~ "-" ]]; then
            echo "${part%-*}"
            return
        else
            echo "$part"
            return
        fi
    done
}

declare -a first_cores
for node in "${NUMA_NODES[@]}"; do
    core=$(get_first_cpu $node)
    first_cores+=($core)
done

# Adjust cores by adding 2
declare -a selected_cores
for core in "${first_cores[@]}"; do
    selected_cores+=($((core + 2)))
done

echo "Detected NUMA nodes: ${NUMA_NODES[*]}"
echo "Selected cores per NUMA node: ${selected_cores[*]}"

# Step 3: Test each loaded latency one by one and store in a matrix
declare -A latency_matrix

echo ""
echo "The following mlc commands will be run to generate the latency matrix:"
printf "\t\tNuma node\n"
printf "Numa node\t"
for node in "${NUMA_NODES[@]}"; do
    printf "%5s\t" "$node"
done
printf "\n"

for i in "${!NUMA_NODES[@]}"; do
    c_core=${selected_cores[$i]}
    printf "%7s\t" "${NUMA_NODES[$i]}"
    for j in "${!NUMA_NODES[@]}"; do
        i_core=${selected_cores[$j]}
        if [[ $i -eq $j ]]; then
            i_core=$((i_core + 1))
        fi
        printf "./mlc --loaded_latency -c$c_core -i$i_core -d0\t"
    done
    printf "\n"
done
echo ""

for i in "${!NUMA_NODES[@]}"; do
    c_core=${selected_cores[$i]}
    for j in "${!NUMA_NODES[@]}"; do
        i_core=${selected_cores[$j]}
        if [[ $i -eq $j ]]; then
            i_core=$((i_core + 1))
        fi
        echo "Testing latency: NUMA node ${NUMA_NODES[$i]} (core $c_core) to NUMA node ${NUMA_NODES[$j]} (core $i_core)"
        output=$($MLC --loaded_latency -c$c_core -i$i_core -d0 2>&1)
        echo "Raw mlc output for -c$c_core -i$i_core:"
        echo "$output"
        latency=$(echo "$output" | awk 'BEGIN{found=0} /[Dd]elay[[:space:]]*\(ns\)[[:space:]]*MB\/sec/{found=1; next} found && NF>=2 {print $2; exit}')
        if [[ -z "$latency" ]]; then
            latency="NA"
        fi
        latency_matrix[$i,$j]=$latency
    done
done

# Step 4: Output latency matrix
printf "\nMeasuring loaded latencies for random access (in ns)...\n"
printf "\t\tNuma node\n"
printf "Numa node\t"
for node in "${NUMA_NODES[@]}"; do
    printf "%5s\t" "$node"
done
printf "\n"

for i in "${!NUMA_NODES[@]}"; do
    printf "%7s\t" "${NUMA_NODES[$i]}"
    for j in "${!NUMA_NODES[@]}"; do
        printf "%7s\t" "${latency_matrix[$i,$j]}"
    done
    printf "\n"
done
