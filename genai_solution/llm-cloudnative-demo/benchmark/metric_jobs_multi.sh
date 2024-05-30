#!/bin/bash

# Arguments
TS=`date +%F-%H-%M-%S`
LOG_PATH=${1:-"mtr_${TS}"}
PIDS=${2:-""}
folder_name=${3:-""}





# init variables
MAIN_PATH="$HOME/llm_metrics"
PID_F="/tmp/metric_jobs.pid"
PGID_F="/tmp/metric_jobs.pgid"

# init the path
mkdir -p "${MAIN_PATH}/${LOG_PATH}/"
cd "${MAIN_PATH}/${LOG_PATH}/"

if [ -n "$folder_name" ]; then
    if [ ! -d "$folder_name" ]; then
        mkdir -p "$folder_name"
        echo "Directory created: $folder_name"
    else
        echo "Directory already exists: $folder_name"
    fi
    cd "${folder_name}"
else
    echo "Directory path is empty or null."
fi


CPU_USAGE=cpuutil.log
MEM_USAGE=memutil.log
MEM_BW=membw.log
MEM_RDT=memrdt.log
CPUS_SET=cpus_set.log
CPU_FREQ=cpu_freq.log




# Set the IFS to a comma (,) to split the string
IFS=','

# Split the PIDS string into an array
read -ra PID_ARRAY <<< "$PIDS"








(
    
  # Iterate over the PIDs and perform some action for each
  for pid in "${PID_ARRAY[@]}"; do
      # Your action here, for example:
      echo "Processing PID: $pid"
      pidstat -u -p ${pid} 1  > ${pid}_${CPU_USAGE} &
      pidstat -r -p ${pid} 1  > ${pid}_${MEM_USAGE} &
      taskset -pc ${pid} > ${pid}_${CPUS_SET} 
      #sudo perf stat -M DRAM_BW_Use -a 2>&1 | tee ${pid}_${MEM_BW} &
      /tmp/mon_bw_by_pid.sh ${pid} > ${pid}_${MEM_RDT} &
      
  done
  sudo turbostat --quiet  --interval 1 > ${CPU_FREQ} &
  /tmp/mon_bw.sh > ${MEM_RDT} &
 
)
pid=$$
echo $pid > ${PID_F}
pgid=`ps -o '%r' $pid | tail -n 1`
echo $pgid > ${PGID_F}




echo "pid=${pid};pgid=${pgid}"
while true; do
  sleep 1
done
# Reset IFS to its default value (space, tab, and newline)
IFS=$' \t\n'