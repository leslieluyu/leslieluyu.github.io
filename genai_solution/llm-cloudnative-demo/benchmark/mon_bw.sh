#!/bin/bash

 

prev_mem_bw_0_local=0
prev_mem_bw_0_total=0
prev_mem_bw_1_local=0
prev_mem_bw_1_total=0

 

while true; do
    sum=0
    value_1=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_00/llc_occupancy)
    value_2=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_01/llc_occupancy)

 

    mem_bw_0_local=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_00/mbm_local_bytes)
    mem_bw_0_total=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_00/mbm_total_bytes)
    mem_bw_1_local=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_01/mbm_local_bytes)
    mem_bw_1_total=$(cat /sys/fs/resctrl/cri-resmgr.high/mon_data/mon_L3_01/mbm_total_bytes)

 

    mem_bw_0_local_mb=$((($mem_bw_0_local - $prev_mem_bw_0_local) / 1024 / 1024))
    mem_bw_0_total_mb=$((($mem_bw_0_total - $prev_mem_bw_0_total) / 1024 / 1024))
    mem_bw_1_local_mb=$((($mem_bw_1_local - $prev_mem_bw_1_local) / 1024 / 1024))
    mem_bw_1_total_mb=$((($mem_bw_1_total - $prev_mem_bw_1_total) / 1024 / 1024))

 

    echo "mem_bw_0_local: $mem_bw_0_local_mb MB"
    echo "mem_bw_0_total: $mem_bw_0_total_mb MB"
    echo "mem_bw_1_local: $mem_bw_1_local_mb MB"
    echo "mem_bw_1_total: $mem_bw_1_total_mb MB"
    prev_mem_bw_0_local=$mem_bw_0_local
    prev_mem_bw_0_total=$mem_bw_0_total
    prev_mem_bw_1_local=$mem_bw_1_local
    prev_mem_bw_1_total=$mem_bw_1_total

 

    value_1_mb=$(echo "scale=2; $value_1 " | bc)
    value_2_mb=$(echo "scale=2; $value_2 " | bc)

 

    sum=$(echo "scale=2; $sum + $value_1_mb + $value_2_mb" | bc)

 

    echo "Socket0 Cache: $value_1_mb"

    echo "Socket1 Cache: $value_2_mb"
    echo "Total: $sum"
    echo "----------------------------"

 

    sleep 1
done
