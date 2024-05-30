#!/bin/bash

# Get the log file path from the command line argument
mem_pattern=${1:-"mem_bw_0_total"}
directory=${2:-"."}
filepattern="memrdt.log"

# Check if a log file path was provided as a command line argument
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <mem_pattern> <directory>"
    exit 1
fi



# Loop through all cpuutil.log files in the directory
#`find ${directory} -type f -name ${filepattern}`
for file in `find ${directory} -type f -name ${filepattern}`; do
    #echo "mem_pattern=${mem_pattern},file=$file"    
    # Use grep to filter lines containing "mem_bw_0_total:" and awk to calculate the average
    
    #find /home/ansible/yulu/chatGLM/bench_result/0927_chatglm2_int4_token39_221/ -type f -name "memrdt.log" -exec grep "mem_bw_0_total" {} +

    newfile=`echo ${file} |awk -F/ '{print $(NF-1) "/" $NF}'`

    #average=$(grep "${mem_pattern}:" "$file"|tail -n +2 | head -n -3 | awk -F'[: ]+' '{ sum += $2; count++ } END { avg = sum / count; print avg }')
    average=$(grep "${mem_pattern}:" "$file"|tail -n +2 | head -n -5 | awk -F'[: ]+' '{ sum += $2; count++ } END { avg = sum / count; print avg }')
    
    # Print the average for the current file
    echo "Average Memory for $newfile: $average MB"
done
