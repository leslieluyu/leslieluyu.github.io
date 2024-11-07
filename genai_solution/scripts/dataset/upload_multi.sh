#!/bin/bash

# Default parameters (will be overridden if provided)
concurrency=
max_uploads=
dataprep_svc_ip=

# Parse command line arguments for parameters
while getopts "c:u:i:" opt; do
    case $opt in
        c) concurrency=$OPTARG ;;  # Changed from max_jobs to concurrency
        u) max_uploads=$OPTARG ;;
        i) dataprep_svc_ip=$OPTARG ;;
        *) echo "Usage: $0 -c <concurrency> -u <max_uploads> -i <dataprep_svc_ip>" >&2; exit 1 ;;
    esac
done

# Check if required parameters are provided
if [ -z "$concurrency" ] || [ -z "$max_uploads" ] || [ -z "$dataprep_svc_ip" ]; then
    echo "Error: All parameters -c (concurrency), -u (max_uploads), and -i (dataprep_svc_ip) are required." >&2
    exit 1
fi

# Log file setup
log_file="upload_log_$(date +%Y%m%d_%H%M%S).log"
exec > "$log_file" 2>&1  # Redirect stdout and stderr to log file

echo "Starting upload script with the following parameters:"
echo "Concurrency: $concurrency"
echo "Max Uploads: $max_uploads"
echo "DataPrep Service IP: $dataprep_svc_ip"

base_dir="/home/yulu/OPEA/PubMed/datasets/datasets/pubmed/chunk/"  # Base directory containing the files
upload_url="http://${dataprep_svc_ip}:6007/v1/dataprep"

# List all relevant files in the directory
files=("$base_dir"pubmed23n*.txt)  # Adjust the pattern as needed

# Check if there are any files to upload
if [ ${#files[@]} -eq 0 ]; then
    echo "No files found to upload."
    exit 1
fi

# Record the start time of the script
script_start_time=$(date +%s)

# Function to upload a file
upload_file() {
    local local_file="$1"
    
    echo "Starting upload for: $local_file"
    start_time=$(date +%s)  # Record start time for this upload
    
    # Perform the upload
    response=$(time (curl -X POST "$upload_url" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@$local_file" 2>&1)
    )
    
    end_time=$(date +%s)  # Record end time for this upload
    elapsed_time=$(( end_time - start_time ))  # Calculate elapsed time for this upload in seconds
    
    # Calculate total elapsed time since the script started
    total_elapsed_time=$(( end_time - script_start_time ))
    
    echo "Uploaded file: $local_file"
    echo "Response from server: $response"
    echo "Time taken for this upload: ${elapsed_time} seconds"
    echo "Total elapsed time since script started: ${total_elapsed_time} seconds"

    # Log the filename when ingestion is finished
    echo "Finished ingestion of file: $local_file" >> "$log_file"

    # Sleep for 2 seconds after each upload
    sleep 2
}

# Loop through each file and upload it in the background
upload_count=0  # Initialize counter for uploaded files

for local_file in "${files[@]}"; do
    if (( upload_count >= max_uploads )); then
        echo "Reached maximum upload limit of $max_uploads files. Stopping."
        break  # Stop if the max uploads limit is reached
    fi
    
    upload_file "$local_file" &  # Start upload in background
    
    # Increment the counter for uploaded files
    ((upload_count++))

    # Control the number of concurrent jobs based on concurrency limit
    while (( $(jobs -r | wc -l) >= concurrency )); do
        wait -n  # Wait for any job to finish
    done
done

# Wait for all remaining background jobs to finish
wait

echo "All file uploads completed."