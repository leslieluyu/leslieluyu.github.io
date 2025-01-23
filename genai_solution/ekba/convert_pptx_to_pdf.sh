#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <directory>"
    echo "Convert all PPTX files in the specified directory to PDF."
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    usage
fi

# Get the input directory
INPUT_DIR="$1"

# Check if the input is a valid directory
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: '$INPUT_DIR' is not a valid directory."
    usage
fi

# Change to the input directory
cd "$INPUT_DIR" || exit

# Convert all PPTX files to PDF using LibreOffice
for pptx_file in *.pptx; do
    if [ -f "$pptx_file" ]; then
        echo "Begin convert: $pptx_file to PDF."
        libreoffice --headless --convert-to pdf "$pptx_file"
        echo "End converted: $pptx_file to PDF."
    else
        echo "No PPTX files found in the directory."
    fi
done

echo "Conversion complete."

