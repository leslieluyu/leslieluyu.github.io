#!/bin/bash

# Define variables
dataprep_svc_ip="172.21.51.89"  # Replace with your actual service IP
base_dir="/home/yulu/OPEA/PubMed/datasets/datasets/pubmed/chunk/"  # Base directory containing the files
upload_url="http://${dataprep_svc_ip}:6007/v1/dataprep"

# List all relevant files in the directory
files=("$base_dir"pubmed23n*.txt)  # Adjust the pattern as needed

# Check if there are any files to upload
if [ ${#files[@]} -eq 0 ]; then
    echo "No files found to upload."
    exit 1
fi

# Maximum number of concurrent uploads
max_jobs=4  # Set the desired limit here

# Maximum number of files to upload
max_uploads=4  # Set the desired maximum upload limit here

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

    # Control the number of concurrent jobs
    while (( $(jobs -r | wc -l) >= max_jobs )); do
        wait -n  # Wait for any job to finish
    done
done

# Wait for all remaining background jobs to finish
wait

echo "All file uploads completed."
