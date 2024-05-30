#!/bin/bash

WORKER_NODE_IP="172.16.28.130"
FOLDER_PREFIX="/home/ansible/yulu/chatGLM/bench_result_r028s013/llm_metrics/"
FILE_UNIQ_NAME=`cat ./FILE_UNIQ_NAME`
RESULT_FILE="metric_result.${FILE_UNIQ_NAME}"

# 0. sync the logs
rsync -r ${WORKER_NODE_IP}:~/llm_metrics /home/ansible/yulu/chatGLM/bench_result_r028s013/ -P

{
# 0. get the FILE_UNIQ_NAME

echo "FILE_UNIQ_NAME=${FILE_UNIQ_NAME}" 



# 2 set LOGFILE,FOLDER,RESULT_FILE
LOGFILE=${FILE_UNIQ_NAME}
FOLDER=${FOLDER_PREFIX}${FILE_UNIQ_NAME}/
#LOGFILE="multi_deploy.log.20240201171948_qcvq"
#FOLDER=${FOLDER_PREFIX}mtr_20240201171948_qcvq_scenario014/




echo "LOGFILE=${LOGFILE}" 
echo "FOLDER=${FOLDER}" 
echo "RESULT_FILE=${RESULT_FILE}" 



# 3 get the scenario from log
echo -e "\n\n\n------ scenario ------" 
grep "info=name:" $LOGFILE |grep -oP "{.*}"|sed "s/'/\"/g" |jq -r '"\(.name)_\(.framework)_\(.dtype)"' 

# 4 get latency from log

# prompt_tokens: completion_tokens: total_dur_s total_token_latency_s  first_token_latency_ms next_token_latency_ms avg_token_latency_ms
echo -e "\n\n\n------ Latency Metric ------" 
echo "prompt_tokens,completion_tokens,total_dur_s,total_token_latency_s,first_token_latency_ms,next_token_latency_ms,avg_token_latency_ms"
grep "The Average Metrics Value of Current Scenario is" $LOGFILE | awk -F': ' '{print $2}' 

#grep "response_data=" $LOGFILE | grep -oP "{.*}" | awk -F'[:,]' '{print $8, $10, $12, $14, $16, $18, $20, $22}' 


# 5 get memory Bandwidth value
echo -e "\n\n\n------ Memory Bandwidth Value ------" 
find $FOLDER -name "memrdt.log"|sort|xargs -I {} python3 process_metrics.py -t MEMBW  -m {} 2>&1 |grep -E "Total Maximum mem_bw_total"|awk -F'[[:space:]]+' '{print $4}'  

# 6 get Cpu Util value
echo -e "\n\n\n------ Cpu Utility Value ------" 
find $FOLDER -name "cpu_freq.log"|sort|xargs -I {} python process_metrics.py -f {} -t CPUUTIL  2>&1 |grep "max_cpu"  


find $FOLDER -name "cpu_freq.log"|sort|xargs -I {} python process_metrics.py -f {} -t CPUUTIL  2>&1 |grep "max_cpu"|awk -F'[:,]' '/avg_cpu/ {print $4}'  

# 7 get Memory Util Value
echo -e "\n\n\n------ Memory Utility Value ------" 
find $FOLDER -name "*memutil.log"|sort|xargs -I {} grep "Average" {}|awk '{print $7,$8}'  

} | tee -a ${RESULT_FILE}