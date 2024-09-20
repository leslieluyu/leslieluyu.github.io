#!/bin/bash
 
out=${1:-out}
mkdir -p $out
source /opt/emon/sep_vars.sh
 
delay=1
duration=20
line="------------------------------------------------"
echo ${line}
echo "Sleeping for ${delay} secs"
sleep ${delay}
echo ${line}
echo ${line} >> ${out}/emon.log
echo "EMON Command: nohup emon -collect-edp -f emon.dat & sleep ${duration}; emon -stop" >> ${out}/emon.log
 
start_emon_time=$(date)
echo "Start EMON: ${start_emon_time}" >> ${out}/emon.log
emon -collect-edp > ${out}/emon.dat & sleep ${duration}
 
emon -stop
 
sudo dmidecode > ${out}/dmidecode.txt
stop_emon_time=$(date)
echo "Stop EMON: ${stop_emon_time}" >> ${out}/emon.log
 
echo ${line}
echo ${line} >> ${out}/emon.log
