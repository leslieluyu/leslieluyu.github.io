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

# Loop through each file and upload it
for local_file in "${files[@]}"; do
    time curl -X POST "$upload_url" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@$local_file"
    sleep 5 
    echo "Uploaded file: $local_file"
done

echo "All file uploads completed."
