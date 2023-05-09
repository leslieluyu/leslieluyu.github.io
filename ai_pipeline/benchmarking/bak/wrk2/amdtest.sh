#!/bin/bash

FRONTEND=${1:-"10.233.52.57"}

# Make sure cpu power policy setting to performance
# ansible -i hosts emon --become -m shell -a "cpupower frequency-info"
#ansible -i hosts emon --become -m shell -a "cpupower frequency-set -g performance"
# ansible -i hosts emon --become -m shell -a "cpupower frequency-info"

# Collect server info
ansible -i hosts emon -m shell -a "mkdir serverinfo"
ansible -i hosts emon --become -m shell -a "dmidecode > serverinfo/dmidecode.txt"
ansible -i hosts emon --become -m shell -a "svr_info --out serverinfo"
ansible -i hosts emon -m fetch -a "src=serverinfo/dmidecode.txt dest=serverinfo/"
ansible -i hosts emon -m fetch -a "src=serverinfo/serverinfo.tgz dest=serverinfo/"

# prepare the emon collection
#ansible -i hosts all -m copy -a "src=runemon.sh dest=runemon.sh mode=0755"
#ansible -i hosts all -m copy -a "src=clx-2s-events.txt dest=clx-2s-events.txt"

for rps in `seq 1500 500 6000`
do
  TT=`date +%F-%H-%M-%S`
  echo "docker exec wrk2 sh /client/test.sh $FRONTEND $rps $TT"
  docker exec wrk2 sh /client/test.sh $FRONTEND ${rps} $TT
  
  echo "Sleep 5 seconds before next run"
  sleep 5
#  echo "Collecting EMON data"
#  ansible -i hosts emon -m shell -a "sudo ./runemon.sh emon$rps"

#  echo "Sleep another 60 seconds to make sure the previous run exit"
#  sleep 60
  
#  echo "Copy dat files"
#  mkdir -p emon${rps}
#  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-v.dat dest=emon${rps}/"
#  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-M.dat dest=emon${rps}/"
#  ansible -i hosts emon -m fetch -a "src=emon${rps}/emon.dat dest=emon${rps}/"
done

