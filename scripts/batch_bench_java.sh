#!/bin/bash

CMD="sudo -E /home/ansible/yulu/grpc1.54.0/tools/run_tests/run_performance_tests.py -l java --category scalable -r"
COUNT=${1:-11}
SCENARIO=${2:-"java_protobuf_async_unary_qps_unconstrained_insecure"}
OUT=${3:-"/home/ansible/yulu/false_sharing/grpc_java"}
dt=`TZ='Asia/Shanghai' date "+%m%d%H%M%S"`


echo "count=${COUNT}"
for i in $(seq 1  ${COUNT})
#for i in {1..${COUNT}}  
do  
    num=`printf "%02d" $i`
    echo "i= $num";  
    $CMD $SCENARIO 2>&1| tee ${OUT}/${dt}_${num}_${SCENARIO}.log
done  


echo "All commands executed successfully."
