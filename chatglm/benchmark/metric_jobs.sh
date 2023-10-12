#!/bin/bash
pids=()

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







(
    if [ -z "$PIDS" ] || [ "$PIDS" == "" ]; then
      # PIDS is empty
      sar -u 1 > ${CPU_USAGE} &
    else
      # PIDS is not empty
      pidstat -u -p ${PIDS} 1  > ${CPU_USAGE} &
      taskset -pc ${PIDS} > ${CPUS_SET} 
    fi
    
    sudo perf stat -M DRAM_BW_Use -a 2>&1 | tee ${MEM_BW} &

    /tmp/mon_bw.sh > ${MEM_RDT} &
 
    
    pids+=("$!")

)
pid=$$
echo $pid > ${PID_F}
pgid=`ps -o '%r' $pid | tail -n 1`
echo $pgid > ${PGID_F}




echo "pid=${pid};pgid=${pgid}"
while true; do
  sleep 1
done