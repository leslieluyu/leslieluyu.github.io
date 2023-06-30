#!/bin/bash

BIN_MAP="/home/ansible/yulu/perf-map-agent/bin/create-java-perf-map.sh"

# Check if scenario argument is provided
if [[ $# -ne 1 ]]; then
	    echo "Error: Scenario argument missing."
	        echo "Usage: $0 <scenario>"
		    exit 1
fi

scenario=$1
out=${2:-"/home/ansible/yulu/cifs_data/luyu/false_sharing/grpc_java/spr/"}

dt=`TZ='Asia/Shanghai' date "+%m%d%H%M%S"`
c_id=`ps -ef | grep io.grpc.benchmarks.driver.LoadWorker | grep 10410 | awk '{print $2}'`
s_id=`ps -ef | grep io.grpc.benchmarks.driver.LoadWorker | grep 10400 | awk '{print $2}'`

# Check if c_id or s_id is null or empty
if [[ -z $c_id || -z $s_id ]]; then
	    echo "Error: c_id or s_id is empty or not found."
	        exit 1
fi

echo "c_id = $c_id, s_id = $s_id"




# export symbols
#${BIN_MAP} $c_id
#${BIN_MAP} $s_id
#ls /tmp/*${c_id}*.map
#ls /tmp/*${s_id}*.map
#echo "finish export the symbols of ${c_id} ${s_id}"

# Command 1
echo "perf c2c record the ${scenario}_client_${dt} "
sudo perf c2c record -a -u --ldlat 50 -p $c_id -o ${scenario}_client_$dt -- sleep 30 &
#sudo sh -c "ulimit -nH; perf c2c record -a -u --ldlat 50 -p $c_id -o ${scenario}_client_$dt -- sleep 30 &"
pid1=$!

sleep 2

# Command 2
echo "perf c2c record the ${scenario}_server_${dt} "
sudo perf c2c record -a -u --ldlat 50 -p $s_id -o ${scenario}_server_$dt -- sleep 30 &
pid2=$!

# Wait for both commands to finish
wait
#wait $pid1
#wait $pid2


echo "wait for the client $c_id"
wait $c_id
echo "the client $c_id is stopped ..."
echo "wait for the client $s_id"
wait $s_id
echo "the client $s_id is stopped ..."


echo "sleep 20 seconds.... for perf record to finish "
sleep 20
# Process output files in parallel
{
    echo "process the ${scenario}_client_${dt} "
    sudo perf c2c report -NN -g --call-graph --full-symbols -c pid,iaddr --stdio -i ${scenario}_client_${dt} > ${out}/${scenario}_client_${dt}.txt
} &

{
    echo "process the ${scenario}_server_${dt} "
    sudo perf c2c report -NN -g --call-graph --full-symbols -c pid,iaddr --stdio -i ${scenario}_server_${dt}  > ${out}/${scenario}_server_${dt}.txt
} &

# Wait for both report commands to finish
wait

echo "All commands executed successfully."
