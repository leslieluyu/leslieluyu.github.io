#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 collection_name [base_directory] [upload_url]"
    echo
    echo "Parameters:"
    echo "  collection_name : (Required) Name of the collection to upload to"
    echo "  base_directory  : Directory containing PDF files to upload"
    echo "                    (default: /home/sdp/yulu/test_docs/EKBA-Product_reference/general/)"
    echo "  upload_url      : URL endpoint for file upload"
    echo "                    (default: http://localhost:6007/v1/dataprep)"
    echo
    echo "Example:"
    echo "  $0 intel_product"
    echo "  $0 intel_product /path/to/files/"
    echo "  $0 intel_product /path/to/files/ http://custom-server:6007/v1/dataprep"
    exit 1
}

# Check if help is requested
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    usage
fi

# Check if collection_name is provided
if [ -z "$1" ]; then
    echo "Error: collection_name is required"
    usage
fi

# Parse command line arguments with defaults
collection_name="$1"  # Required parameter
dataprep_svc_ip="localhost"  # Replace with your actual service IP
base_dir=${2:-"/home/sdp/yulu/test_docs/EKBA-Product_reference/general/"}  # Default base directory
upload_url=${3:-"http://${dataprep_svc_ip}:6007/v1/dataprep"}  # Default upload URL
delete_url=${3:-"http://${dataprep_svc_ip}:6007/v1/dataprep/delete_file"}  # Default upload URL

# Validate base_dir exists
if [ ! -d "$base_dir" ]; then
    echo "Error: Directory '$base_dir' does not exist"
    usage
fi

# Display configuration
echo "Using configuration:"
echo "Collection name: $collection_name"
echo "Base directory: $base_dir"
echo "Upload URL: $upload_url"

# Remember the current directory
current_directory=$(pwd)

# Change to the input directory
cd "$base_dir" || exit

# List all relevant files in the directory
shopt -s globstar  # Enable recursive globbing
files=(**/*.pdf)  # Adjust the pattern as needed

# Check if there are any files to upload
if [ ${#files[@]} -eq 0 ]; then
    echo "No files found to upload."
    exit 1
fi

# Record the start time
total_start_time=$(date +%s)

# Loop through each file and upload it
for local_file in "${files[@]}"; do
    start_time=$(date +%s)
    #1. delete the file from vectorDB
    echo "Will delete file: $local_file "

    time curl -X POST  "$delete_url" \
       -H "Content-Type: application/json"  \
       -d "{\"file_path\": \"$local_file\", \"collection_name\":\"$collection_name\"}"
    echo "Deleted file: $local_file "

    #2. upload the file to the vectorDB
    echo "Will upload file: $local_file "
    time curl -X POST "$upload_url" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@$local_file" \
        -F "collection_name=$collection_name"
    end_time=$(date +%s)
    time_spent=$((end_time - start_time))
    echo "Uploaded file: $local_file in $time_spent seconds"
    sleep 5
done
# Calculate total time spent
total_end_time=$(date +%s)
total_time_spent=$((total_end_time - total_start_time))


# Change back to the original directory
cd "$current_directory"

echo "All file uploads completed in $total_time_spent seconds."
