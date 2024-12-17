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
command="./stresscli.py load-test --profile run-v1.0-16-ql.yaml"
DATA_FILE_PATH="/home/yulu/OPEA/test_docs/pubmed"
file_names=("pubmed_10.txt" "pubmed_100.txt" "pubmed_1000.txt" "pubmed_10000.txt")
max_lines=("10" "100" "100" "1000")
batch_sizes=(1 2 4 8 16 32 64 128)
max_tokens=(64 128 256 512 1024)
#file_names=("pubmed_100.txt")
#max_lines=("100")
batch_sizes=(1 2 4 8 "")
# max_tokens=(64)






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

    if [[ -z "$value" ]]; then
        # If value is empty, remove the key from the ConfigMap
        echo "Value is empty. Removing key '$key' from ConfigMap '$configmap_name'." 2>&1 | tee -a "$logfile"
        kb patch configmap "$configmap_name" --type='json' -p="[{\"op\": \"remove\", \"path\": \"/data/$key\"}]" 2>&1 | tee -a "$logfile"
    else
        # If value is not empty, update the key with the new value
        kb patch configmap "$configmap_name" --type='json' -p="[{\"op\": \"replace\", \"path\": \"/data/$key\", \"value\": \"$value\"}]" 2>&1 | tee -a "$logfile"
    fi

    # kb patch configmap "$configmap_name" --type='json' -p="[{\"op\": \"replace\", \"path\": \"/data/$key\", \"value\": \"$value\"}]" 2>&1 | tee -a "$logfile"

    end_time=$(date +%s)  # End time for logging
    duration=$((end_time - start_time))
    echo "Finished patching ConfigMap '$configmap_name'. Time spent: $duration seconds." 2>&1| tee -a "$logfile" 
}


redeploy_pods() {
    local namespace="$1"
    local deployment_name="$2"
    local wait_time="$3"
    # Get the desired number of replicas from the deployment
    local desired_replicas
    desired_replicas=$(kubectl -n "$namespace" get deployment "$deployment_name" -o jsonpath='{.spec.replicas}')
    echo "Desired replicas: $desired_replicas in deployment $deployment_name namespace $namespace" | tee -a "$logfile" 2>&1

    kubectl -n "$namespace" scale deployment "$deployment_name" --replicas=0 
    sleep ${wait_time}
    kubectl -n "$namespace" scale deployment "$deployment_name" --replicas="${desired_replicas}"
    sleep ${wait_time}
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

    # kubectl -n "$namespace" scale deployment "$deployment_name" --replicas=0 
    # sleep 10
    # kubectl -n "$namespace" scale deployment "$deployment_name" --replicas="${desired_replicas}"
    # sleep 10

    while true; do
        # Get the number of ready pods
        local ready_pods
        # ready_pods=$(kubectl -n "$namespace" get pods  -l "$app_label" --field-selector=status.phase=Running -o jsonpath='{.items[?(@.status.phase=="Running")].status.containerStatuses[*].ready}' |tr ' ' '\n'| grep -c true)
        ready_pods=$(kb get pods -l "$app_label" --field-selector=status.phase=Running -o json | jq -r '.items[] | select(.metadata.deletionTimestamp == null) | .status.containerStatuses[].ready' | grep -c true)
        terminating_pods=$(kb get pods -l "$app_label" -o json | jq '[.items[] | select(.metadata.deletionTimestamp != null)] | length')
        # get_pods_status "$app_label"
        echo "Ready pods: $ready_pods, Desired replicas: $desired_replicas", Terminating pods: ${terminating_pods} | tee -a "$logfile" 2>&1

        # Check if all pods are ready and match the desired replicas
        if [[ "$ready_pods" -eq "$desired_replicas" && "$terminating_pods" -eq 0 ]]; then
            echo "All pods are ready and no pods are terminating." | tee -a "$logfile" 2>&1
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


# Initialize variables
script_start_time=$(date +%s)

# Function to log messages
log_message() {
    local message="$1"
    echo -e "$message" 2>&1 | tee -a "$logfile"
}

# Function to handle errors
handle_error() {
    local message="$1"
    log_message "ERROR: $message"
    exit 1
}


patch_redeploy_wait() {
    local cm="$1"
    local env_key="$2"
    local env_value="$3"
    local namespace="$4"
    local deployment_name="$5"
    local label_pod="$6"
    local timeout="$7"
    local interval="$8"

    # Step 1: Patch configmap max_tokens in LLM-TGI
    log_message "======  ｜-- Started Patch_confimap $cm."
    patch_configmap "$cm" "$env_key" "$env_value" || handle_error "Failed to patch configmap $cm"
    log_message "======  ｜-- Finished Patch_confimap $cm."

    # Step 2: Redeploy the TGI
    log_message "======  ｜-- Started redeploying $deployment_name."
    start_time=$(date +%s)
    redeploy_pods "$namespace" "$deployment_name" 10 || handle_error "Failed to redeploy $deployment_name"
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    log_message "======  ｜-- Finished redeploying $deploy_tgi. Time spent: $duration seconds."

    # Step 3: Wait for pods to be ready
    log_message "======  ｜-- Started wait_for_pods_ready $deployment_name."
    wait_for_pods_ready_real "$namespace" "$deployment_name" "$label_pod" "$timeout" "$interval" || handle_error "Failed to wait for $deployment_name pods to be ready"
    get_pods_status "$label_pod"
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    log_message "======  ｜-- Finished wait_for_pods_ready $deployment_name ready! Time spent: $duration seconds."
}

# Main job function
do_main_job() {
    log_message "\n\n====== All operations started. [file_names:${file_names[*]},MAX_LINES:(${max_lines[*]}),MAX_BATCH_SIZE:(${batch_sizes[*]}),MAX_TOKENS:(${max_tokens[*]})]. Logs saved in $logfile. \n\n"  
    # Nested loops to iterate through each combination
    log_message "====== Started ALL file_names:(${file_names[*]}),ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]}) " 
    total_round=$((${#file_names[@]} * ${#batch_sizes[@]} * ${#max_tokens[@]}))
    current_round=0
    
    for file_name in "${file_names[@]}"; do
        # Step 0: Ingest the dataset
        start_time=$(date +%s)
        log_message "======  ｜- Started ingest_data  $file_name. " 
        ingest_data "$file_name" 
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_message "======  ｜- Finished ingest_data  $file_name. Time spent: $duration seconds." 

        for bs in "${batch_sizes[@]}"; do

            # Step 1: Patch configmap max_tokens in TGI, Redeploy the TGI  to wait for the pods to be ready
            patch_redeploy_wait "$CM_TGI" "MAX_BATCH_SIZE" "$bs" "$namespace" "$DEPLOY_TGI" "$LABEL_TGI" "$timeout" "$interval"

            for max_token in "${max_tokens[@]}"; do
                round_start_time=$(date +%s)
                ((current_round++))
                round_info="round: ${current_round}/${total_round}"

                log_message "====== Started a ${round_info} [file_name:${file_name},MAX_LINES:${max_line},MAX_BATCH_SIZE:${bs},MAX_TOKENS:${max_token}]."

                # Step 2: Patch configmap max_tokens in LLM-TGI, Redeploy the LLM-TGI to wait for the pods to be ready
                patch_redeploy_wait "$CM_LLM" "MAX_TOKENS" "$max_token" "$namespace" "$DEPLOY_LLM" "$LABEL_LLM" "$timeout" "$interval"



                # Step 3: Set QLIST RANDOM environment variable (if needed)
                log_message "======${round_info} 1. Started set MAX_LINES:${max_line}"
                export MAX_LINES=${max_line}
                log_message "======${round_info} 1. Finished set MAX_LINES:${max_line}"

                # Step 4: Execute the command
                log_message "======${round_info} 2. Started Executing: $command."
                start_time=$(date +%s)
                eval "$command" 2>&1 | tee -a "$logfile" || handle_error "Failed to execute command: $command"
                end_time=$(date +%s)
                duration=$((end_time - start_time))
                log_message "======${round_info} 2. Finished Executing: $command. Time spent: $duration seconds."

                round_end_time=$(date +%s)
                round_duration=$((round_end_time - round_start_time))
                script_end_time=$(date +%s)
                total_duration=$((script_end_time - script_start_time))
                log_message "====== Finished a ${round_info} [file_name:${file_name},MAX_LINES:${MAX_LINES},MAX_BATCH_SIZE:${bs},MAX_TOKENS:${max_token}]. Round Time spent: $round_duration seconds. Total time spent: $total_duration seconds.\n\n"
            done
            log_message "====== Finished ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line},MAX_BATCH_SIZE:${bs}"
        done
        log_message "====== Finished ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]}) ... file_name:${file_name},MAX_LINES:${max_line}"
    done
    log_message "====== Finished ALL file_names:(${file_names[*]}),ALL batch_sizes:(${batch_sizes[*]}),ALL Max_tokens:(${max_tokens[*]})"

    # Calculate total duration since script started
    script_end_time=$(date +%s)
    total_duration=$((script_end_time - script_start_time))
    log_message "\n\n\n\n====== All operations completed. Total time spent: $total_duration seconds. Logs saved in $logfile."
}

# Main function
main() {
    echo "Welcome to the script!"

    # Call functions
    patch_configmap "$CM_LLM" "MAX_TOKENS" "${max_tokens[0]}" || handle_error "Failed to patch configmap $CM_LLM"
    patch_configmap "$CM_TGI" "MAX_BATCH_SIZE" "${batch_sizes[0]}" || handle_error "Failed to patch configmap $CM_TGI"
}

# Call the main function
# main
do_main_job