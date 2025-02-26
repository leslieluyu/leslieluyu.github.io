#!/bin/bash

. base.sh
FRONTEND1=${1:-"10.107.83.125"}
FRONTEND2=${2:-"10.107.83.125"}
INITRPS=${3:-27000}
ENDRPS=${4:-35000}
NS1="gms-ctl0"
NS2="gms-ctl1"
# Usually this will be put at the first run, no need to run here

# Make sure cpu power policy setting to performance
#ansible -i hosts emon --become -m shell -a "cpupower frequency-info"
#ansible -i hosts emon --become -m shell -a "cpupower frequency-set -g performance"
#ansible -i hosts emon --become -m shell -a "cpupower frequency-info"
# Collect server info
#mkdir svrinfo
#svr_info --targets ./targets --out svrinfo

# DIFF for BM intel/amd/arm
# prepare the emon collection, Intel only
ansible -i hosts emon -m copy -a "src=runemon.sh dest=runemon.sh mode=0755"
ansible -i hosts emon -m copy -a "src=sapphirerapids_server_events_private.txt dest=sapphirerapids_server_events_private.txt"

for rps in `seq ${INITRPS} 500 ${ENDRPS}`
do
  TT=`date +%F-%H-%M-%S`
  ansible -i hosts emon -m shell -a "sudo rm -rf emon$rps"
  ansible -i hosts emon -m shell -a "mkdir -p emon$rps"
  echo "docker exec wrk2 sh /client/test.sh $FRONTEND1 and $FRONTEND2 $rps $TT &"
  #docker exec wrk2 sh /client/test.sh $FRONTEND ${rps} $TT &
  docker exec wrk2 sh /client/test.sh $FRONTEND1 ${rps} ${NS1} &
  docker exec wrk2 sh /client/test.sh $FRONTEND2 ${rps} ${NS2} &
  
  echo "Sleep 5 seconds then collect emon data for 30 seconds"
  sleep 5
  echo "Collecting 30 seconds sar data background"
  ansible -i hosts emon -m shell -a "nohup sudo sar -u 1 30 >> emon$rps/cpuutil.log &"
  ansible -i hosts emon -m shell -a "nohup sudo sar -d 1 30 >> emon$rps/diskutil.log &"
  ansible -i hosts emon -m shell -a "nohup sar -n DEV 1 30 >> emon$rps/netutil.log &"
  ansible -i hosts emon -m shell -a "nohup top -b -c -n 10 >> emon$rps/top.log &"

  echo "Collecting EMON data"
# DIFF for BM intel/amd/arm
# For VM and no emon data
#  sleep 30
# For Intel BM to collect emon
  ansible -i hosts emon -m shell -a "sudo ./runemon.sh emon$rps"
# For arm to collect perf stat data
  #ansible -i hosts emon --become -m shell -a "/opt/intel/edp-gvt2_v4/collect-arm-perf 200 30 emon${rps}/perf-output.txt"

  echo "Sleep another 30 seconds to make sure the previous run exit"
  sleep 30
  
  echo "Copy dat files"
  mkdir -p emon${rps}
  ansible -i hosts emon -m fetch -a "src=emon${rps}/cpuutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/diskutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/netutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/top.log dest=emon${rps}/"

# DIFF for BM intel/amd/arm
# For Intel to collect emon
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-v.dat dest=emon${rps}/"
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-M.dat dest=emon${rps}/"
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon.dat dest=emon${rps}/"
# For arm to collect perf stat data
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/perf-output.txt dest=emon${rps}/"
done


