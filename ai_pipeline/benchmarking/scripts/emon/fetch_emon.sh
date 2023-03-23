#!/bin/bash



# DIFF for BM intel/amd/arm
# prepare the emon collection, Intel only
event_file="sapphirerapids_server_events_private.txt"
ansible -i hosts emon -m copy -a "src=runemon.sh dest=runemon.sh mode=0755"


# for sapphirerapids
ansible -i hosts emon -m copy -a "src=${event_file} dest=${event_file}" 

#ansible -i hosts emon -m copy -a "src=sapphirerapids_server_events_private.txt dest=sapphirerapids_server_events_private.txt" 
# for icelake
#ansible -i hosts emon -m copy -a "src=icx-2s-events.txt dest=icx-2s-events.txt" 

for rps in `seq 10000 1 10000`
do
  TT=`date +%F-%H-%M-%S`
  ansible -i hosts emon -m shell -a "sudo rm -rf emon$rps"
  ansible -i hosts emon -m shell -a "mkdir -p emon$rps"
  
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
  ansible -i hosts emon -m shell -a "sudo ./runemon.sh emon$rps ${event_file}"
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
  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-v.dat dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-M.dat dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon.dat dest=emon${rps}/"
# For arm to collect perf stat data
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/perf-output.txt dest=emon${rps}/"
done

