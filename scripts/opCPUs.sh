#!/bin/bash
NUMA=1
CORE=56

for i in $(seq 0 $((CORE-1)))
do
  echo "i=$i"
  cpu1=$((NUMA*CORE+i))
  cpu2=$(((NUMA+2)*CORE+i))
  echo "${cpu1},${cpu2}"
  if [[ "$1" == "enable" ]]; then
     sudo echo 1 > /sys/devices/system/cpu/cpu${cpu1}/online
     sudo echo 1 > /sys/devices/system/cpu/cpu${cpu2}/online
     echo "enable cpu:${cpu1},${cpu2}"
  elif [[ "$1" == "disable" ]]; then
     sudo echo 0 > /sys/devices/system/cpu/cpu${cpu1}/online
     sudo echo 0 > /sys/devices/system/cpu/cpu${cpu2}/online
     echo "disable cpu:${cpu1},${cpu2}"
  elif [[ "$1" == "dryrun" ]]; then
     echo "dryrunning nothing happened ..." 
  else
     echo 'illegal parameter'
  fi
done
