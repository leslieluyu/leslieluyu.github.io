#!/bin/bash

# Arguments
TS=`date +%F-%H-%M-%S`
LOG_PATH=${1:-"mtr_${TS}"}
PIDS=${2:-""}





# init variables
MAIN_PATH="$HOME/llm_metrics"
PID_F="/tmp/metric_jobs.pid"
PGID_F="/tmp/metric_jobs.pgid"

# init the path
mkdir -p "${MAIN_PATH}/${LOG_PATH}/"
cd "${MAIN_PATH}/${LOG_PATH}/"

CPU_USAGE=cpuutil.log
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
      pidstat -u -p ${PIDS} 1  > ${pid}_${CPU_USAGE} &
      taskset -pc ${PIDS} > ${pid}_${CPUS_SET} 
      sudo perf stat -M DRAM_BW_Use -a 2>&1 | tee ${pid}_${MEM_BW} &
      /tmp/mon_bw_by_pid.sh > ${pid}_${MEM_RDT} &
      sudo turbostat --quiet  --interval 1 > ${pid}_${CPU_FREQ}
  done
    



 
  

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