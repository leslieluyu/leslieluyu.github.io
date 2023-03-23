#!/bin/bash

FRONTEND=${1:-"10.96.39.33"}
INITRPS=${2:-5000}
ENDRPS=${3:-15000}

# Make sure cpu power policy setting to performance
# ansible -i hosts emon --become -m shell -a "cpupower frequency-info"
# ansible -i hosts emon --become -m shell -a "cpupower frequency-set -g performance"
# ansible -i hosts emon --become -m shell -a "cpupower frequency-info"

# Collect server info
#ansible -i hosts emon -m shell -a "mkdir serverinfo"
#ansible -i hosts emon --become -m shell -a "dmidecode > serverinfo/dmidecode.txt"
#ansible -i hosts emon --become -m shell -a "svr_info --out serverinfo"
#ansible -i hosts emon -m fetch -a "src=serverinfo/dmidecode.txt dest=serverinfo/"
#ansible -i hosts emon -m fetch -a "src=serverinfo/serverinfo.tgz dest=serverinfo/"

# prepare the emon collection
#ansible -i hosts emon -m copy -a "src=runemon.sh dest=runemon.sh mode=0755"
#ansible -i hosts emon -m copy -a "src=clx-2s-events.txt dest=clx-2s-events.txt"

for rps in `seq ${INITRPS} 1000 ${ENDRPS}`
do
  TT=`date +%F-%H-%M-%S`
  ansible -i hosts emon -m shell -a "sudo rm -rf emon$rps"
  ansible -i hosts emon -m shell -a "mkdir -p emon$rps"
  echo "docker exec wrk2 sh /client/test.sh $FRONTEND $rps $TT &"
  docker exec wrk2 sh /client/test.sh $FRONTEND ${rps} $TT &
  
  echo "Sleep 5 seconds then collect emon data for 30 seconds"
  sleep 5
  echo "Collecting sar data"
  ansible -i hosts emon -m shell -a "nohup sudo sar -u 1 30 >> emon$rps/cpuutil.log &"
  ansible -i hosts emon -m shell -a "nohup sudo sar -d 1 30 >> emon$rps/diskutil.log &"
  ansible -i hosts emon -m shell -a "nohup sar -n DEV 1 30 >> emon$rps/netutil.log &"
  ansible -i hosts emon -m shell -a "nohup top -b -c -n 10 >> emon$rps/top.log &"

  echo "Collecting EMON data"
  sleep 30
  #ansible -i hosts emon -m shell -a "sudo ./runemon.sh emon$rps"

  echo "Sleep another 30 seconds to make sure the previous run exit"
  sleep 30
  
  echo "Copy dat files"
  mkdir -p emon${rps}
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-v.dat dest=emon${rps}/"
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon-M.dat dest=emon${rps}/"
  #ansible -i hosts emon -m fetch -a "src=emon${rps}/emon.dat dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/cpuutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/diskutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/netutil.log dest=emon${rps}/"
  ansible -i hosts emon -m fetch -a "src=emon${rps}/top.log dest=emon${rps}/"
done

