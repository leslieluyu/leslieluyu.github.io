#!/bin/bash

#echo "All Arguments using \$*: $*"
#echo "All Arguments using \$@: $@"
#echo "argument num: $#"
# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <directory_path> <old_extension> <new_extension>"
    exit 1
fi

# Set variables for directory path, old extension, and new extension
directory_path="$1"
old_extension="$2"
new_extension="$3"

# Change to the specified directory
cd "$directory_path" || { echo "Directory not found"; exit 1; }

# Rename files with the specified old extension to the new extension
shopt -s nullglob  # Enable nullglob to avoid issues if no files match
found_files=false
for file in *"$old_extension"; do
    found_files=true
    echo "mv $file to ${file%$old_extension}$new_extension"
    mv "$file" "${file%$old_extension}$new_extension"
done
# After the loop, check if any files were found
if [ "$found_files" = false ]; then
    echo "No files with extension '$old_extension' found in the specified directory."
fi
echo "Renaming completed."





