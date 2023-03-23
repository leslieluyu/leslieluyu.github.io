#!/bin/bash

# Need to put this script to each server's home using
# ansible -i hosts all -m copy -a "src=runemon.sh dest=runemon.sh"
# ansible -i hosts all -m copy -a "src=clx-2s-events.txt dest=clx-2s-events.txt"
out=${1:-out}
mkdir -p $out
. /opt/intel/sep/sep_vars.sh
emon -v > ${out}/emon-v.dat
emon -M > ${out}/emon-M.dat
emon -i icx-2s-events.txt > ${out}/emon.dat & sleep 30 

emon -stop
