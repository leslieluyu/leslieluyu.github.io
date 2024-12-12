#!/bin/bash
# Define a function for kubectl with the specified namespace

kb() {
    kubectl -n benchmark-yulu "$@"
}


# Logfile setup
timestamp=$(date +"%Y%m%d_%H%M%S")
logfile="deployment_log_$timestamp.txt"
# Start time for total duration tracking
script_start_time=$(date +%s)

# Define your variables (example values)
command="./stresscli.py load-test --profile run-v1.0-gaudi-128-ql.yaml"
DATA_FILE_PATH="/home/yulu/OPEA/test_docs/pubmed"

# full combination of all the parameter
file_names=("pubmed_10.txt" "pubmed_100.txt" "pubmed_1000.txt" "pubmed_10000.txt")
max_lines=("10" "100" "100" "1000")
batch_sizes=(1 2 4 8 16 32 64 128)
max_tokens=(64 128 256 512 1024)

# file_names=("pubmed_10.txt")
# max_lines=("10")
# batch_sizes=(1 2)

max_tokens=(64 128)

namespace="benchmark-yulu"
timeout=300  # Timeout in seconds
interval=10  # Interval to check the status
# ConfigMap name
CM_TGI="chatqna-tgi-config"
CM_LLM="chatqna-llm-uservice-config"

DEPLOY_TGI="chatqna-tgi"
DEPLOY_LLM="chatqna-llm-uservice"

LABEL_TGI="app.kubernetes.io/instance=chatqna,app.kubernetes.io/name=tgi"
LABEL_LLM="app.kubernetes.io/instance=chatqna,app.kubernetes.io/name=llm-uservice"

# Function to patch a ConfigMap
patch_configmap() {
    local configmap_name="$1"
    local key="$2"
    local value="$3"
    
    echo "Patching ConfigMap '$configmap_name' with $key=$value..." 2>&1| tee -a "$logfile" 
    start_time=$(date +%s)  # Start time for logging

    kb patch configmap "$configmap_name" --type='json' -p="[{\"op\": \"replace\", \"path\": \"/data/$key\", \"value\": \"$value\"}]" 2>&1 | tee -a "$logfile"

    end_time=$(date +%s)  # End time for logging
    duration=$((end_time - start_time))
    echo "Finished patching ConfigMap '$configmap_name'. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 
}



wait_for_pods_ready_real() {
    local namespace="$1"
    local deployment_name="$2"
    local app_label="$3"
    local timeout="$4"
    local interval="$5"

    # print all the arguments: namespace,deployment_name,app_label,timeout,interval
    echo "wait_for_pods_ready_real: namespace:${namespace},deployment_name:${deployment_name},app_label=${app_label},timeout=${timeout}, interval=${interval}" 2>&1| tee -a "$logfile"



    # Get the desired number of replicas from the deployment
    local desired_replicas
    desired_replicas=$(kubectl -n "$namespace" get deployment "$deployment_name" -o jsonpath='{.spec.replicas}')

    echo "Waiting for pods in deployment '$deployment_name' with namespace '$namespace' to be ready..." | tee -a "$logfile" 2>&1
    echo "Desired replicas: $desired_replicas" | tee -a "$logfile" 2>&1

    local timer=0

    kubectl -n "$namespace" scale deployment "$deployment_name" --replicas=0 
    sleep 10
    kubectl -n "$namespace" scale deployment "$deployment_name" --replicas="${desired_replicas}"
    sleep 10

    while true; do
        # Get the number of ready pods
        local ready_pods
        ready_pods=$(kubectl -n "$namespace" get pods  -l "$app_label" --field-selector=status.phase=Running -o jsonpath='{.items[?(@.status.phase=="Running")].status.containerStatuses[*].ready}' |tr ' ' '\n'| grep -c true)
        get_pods_status "$app_label"
        echo "Ready pods: $ready_pods, Desired replicas: $desired_replicas" | tee -a "$logfile" 2>&1

        # Check if all pods are ready and match the desired replicas
        if [[ "$ready_pods" -eq "$desired_replicas" ]]; then
            echo "All pods are ready." | tee -a "$logfile" 2>&1
            return 0  # Success
        fi

        # Check for timeout
        if [[ $timer -ge $timeout ]]; then
            echo "Timeout reached. Not all pods are ready." | tee -a "$logfile" 2>&1
            return 1  # Failure
        fi

        sleep "$interval"
        ((timer+=interval))
    done
}


# Function to wait for pods to be ready
wait_for_pods_ready() {
    local app_label="$1"
    local timeout="$2"
    
    echo "Waiting for pods with label '$app_label' to be ready..." 2>&1| tee -a "$logfile" 
    start_time=$(date +%s)  # Start time for logging

    kb wait --for=condition=ready pod -l "$app_label" --timeout="$timeout" 2>&1 | tee -a "$logfile"

    kb get pod -l "$app_label" 2>&1 | tee -a "$logfile"

    end_time=$(date +%s)  # End time for logging
    duration=$((end_time - start_time))
    
    if [ $? -eq 0 ]; then
        echo "All pods are ready. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 
    else
        echo "Failed to wait for pods to be ready or timed out. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 
    fi
}

get_pods_status() {
    local app_label="$1"
    kb get pod -l "$app_label" 2>&1 | tee -a "$logfile"
}

ingest_data() {
    local file_name="${DATA_FILE_PATH}/$1"

    start_time=$(date +%s)  # Start time for logging
    # get data_prep_endpoint"
    data_prep_endpoint="`kb get svc|grep data|awk '{print $3}'`:6007" && echo ${data_prep_endpoint}
    # delete files
    curl -X POST     -H "Content-Type: application/json"     -d '{"file_path": "all"}'     ${data_prep_endpoint}/v1/dataprep/delete_file

    curl --noproxy "*" ${data_prep_endpoint}/v1/dataprep -H "Content-Type: multipart/form-data"      -F "files=@${file_name}"

    end_time=$(date +%s)  # End time for logging
    duration=$((end_time - start_time))
    echo "Finished ingest file_name:${file_name}. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 
}





function do_main_job() {

    echo -e "\n\n====== All operations started. [file_names:${file_names[*]},MAX_LINES:(${max_lines[*]}),MAX_BATCH_SIZE:(${batch_sizes[*]}),MAX_TOKENS:(${max_tokens[*]})]. Logs saved in $logfile. \n\n" 2>&1| tee -a "$logfile" 
    # Nested loops to iterate through each combination
    echo -e "====== Started ALL file_names:(${file_names[*]}),ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]}) " 2>&1| tee -a "$logfile"
    for ((i=0; i<${#max_lines[@]}; i++)); do
        echo "---- i=${i}"
        file_name=${file_names[$i]}
        max_line=${max_lines[$i]}
        echo -e "====== Started ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line}" 2>&1| tee -a "$logfile"
        for bs in "${batch_sizes[@]}"; do
            echo -e "====== Started  ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line},MAX_BATCH_SIZE:${bs}" 2>&1| tee -a "$logfile" 
            for max_token in "${max_tokens[@]}"; do
                round_start_time=$(date +%s)
                echo -e "\n\n====== Starteded a round [file_name:${file_name},MAX_LINES:${max_line},MAX_BATCH_SIZE:${bs},MAX_TOKENS:${max_token}]." 2>&1| tee -a "$logfile"
                
                # Step 0: Ingest the dataset
                ingest_data "$file_name" 
                echo -e "====== 0. Finished ingest_data  $file_name. " 2>&1| tee -a "$logfile" 


                # Step 1: Patch the batch_sizes in TGI, and max_tokens in LLM-TGI
                patch_configmap "$CM_TGI" "MAX_BATCH_SIZE" "$bs"
                patch_configmap "$CM_LLM" "MAX_TOKENS" "$max_token"

                echo -e "====== 1. Finished Patch_confimap  $CM_TGI and $CM_LLM " 2>&1| tee -a "$logfile" 

                # Step 2: Redeploy the TGI and LLM-TGI to wait for the pods to be ready
                # echo -e "Redeploying $DEPLOY_TGI..." 2>&1| tee -a "$logfile" 
                # start_time=$(date +%s)
                # kb rollout restart deploy "$DEPLOY_TGI" 2>&1 | tee -a "$logfile"
                # end_time=$(date +%s)
                # duration=$((end_time - start_time))
                # echo -e "====== 2.1 Finished redeploying $DEPLOY_TGI. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 

                # echo -e "Redeploying $DEPLOY_LLM..." 2>&1| tee -a "$logfile" 
                # start_time=$(date +%s)
                # kb rollout restart deploy "$DEPLOY_LLM" 2>&1 | tee -a "$logfile"
                # end_time=$(date +%s)
                # duration=$((end_time - start_time))
                # echo -e "====== 2.2 Finished redeploying $DEPLOY_LLM. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 

                start_time=$(date +%s)

                # wait_for_pods_ready "$LABEL_LLM" "60s"
                # wait_for_pods_ready "$LABEL_TGI" "300s"
                sleep 5
                wait_for_pods_ready_real "$namespace" "$DEPLOY_LLM" "$LABEL_LLM" "$timeout" "$interval"
                get_pods_status "$LABEL_LLM"
                wait_for_pods_ready_real "$namespace" "$DEPLOY_TGI" "$LABEL_TGI" "$timeout" "$interval"
                get_pods_status "$LABEL_TGI"
                end_time=$(date +%s)
                duration=$((end_time - start_time))
                echo -e "====== 2.3 Finished wait_for_pods_ready  Time spent: $duration seconds." 2>&1| tee -a "$logfile" 

                

                # Step 3: Set QLIST RANDOM environment variable (if needed)
                export MAX_LINES=${max_line}
                echo -e "====== 3 Finished set MAX_LINES:${max_line} " 2>&1| tee -a "$logfile" 
                # Step 4: Execute the command
                start_time=$(date +%s)

                eval "$command" 2>&1 | tee -a "$logfile"
                end_time=$(date +%s)
                duration=$((end_time - start_time))
                echo -e "====== 4 Executing: $command. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 

                round_end_time=$(date +%s)
                round_duration=$((round_end_time - round_start_time))
                script_end_time=$(date +%s)
                total_duration=$((script_end_time - script_start_time))
                echo -e "====== Finished a round [file_name:${file_name},MAX_LINES:${MAX_LINES},MAX_BATCH_SIZE:${bs},MAX_TOKENS:${max_token}]. Round Time spent: $round_duration seconds. Total time spent: $total_duration seconds.\n\n " 2>&1| tee -a "$logfile"
            done
            echo -e "====== Finished ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line},MAX_BATCH_SIZE:${bs}" 2>&1| tee -a "$logfile" 
        done
        echo -e "====== Finished ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line}" 2>&1| tee -a "$logfile"
    done
    echo -e "====== Finished ALL file_names:(${file_names[*]}),ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]})" 2>&1| tee -a "$logfile"

    # Calculate total duration since script started
    script_end_time=$(date +%s)
    total_duration=$((script_end_time - script_start_time))
    echo -e "\n\n\n\n====== All operations completed. Total time spent: $total_duration seconds. Logs saved in $logfile." 2>&1| tee -a "$logfile" 
}


# Main function
main() {
    echo "Welcome to the script!"
    
    # Call functions
    patch_configmap "$CM_LLM" "MAX_TOKENS" "${max_tokens[0]}"
    patch_configmap "$CM_TGI" "MAX_BATCH_SIZE" "${batch_sizes[0]}"
}

# Call the main function
# main
do_main_job