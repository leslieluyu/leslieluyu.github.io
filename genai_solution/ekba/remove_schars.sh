# for file in *; do
#     # Remove single quotes and replace spaces with underscores
#     new_file=$(echo "$file" | sed "s/^'//; s/'\$//; s/ /_/g")
#     #echo ${new_file} 
#     # Check if the new filename is different from the original
#     if [[ "$file" != "$new_file" ]]; then
#          echo "will mv $file to $new_file"
#          mv "$file" "$new_file"
      
#     fi
# done

# add parameters for input directory
#!/bin/bash

# Check if the input directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <input_directory>"
    exit 1
fi

input_directory="$1"
# Define the pattern to be replaced
pattern="[ ()&【】]"

# Remember the current directory
current_directory=$(pwd)

# Change to the input directory
cd "$input_directory" || exit

for file in *; do
    # Remove single quotes and replace spaces with underscores
    # new_file=$(echo "$file" | sed "s/^'//; s/'\$//; s/ /_/g")
    # new_file=$(echo "$file" | sed "s/^'//; s/'\$//; s/ /_/g; s/)/_/g; s/&/_/g")
    new_file=$(echo "$file" | sed "s/^'//; s/'\$//; s/$pattern/_/g")

    #echo ${new_file} 
    # Check if the new filename is different from the original
    if [[ "$file" != "$new_file" ]]; then
         echo "will mv $file to $new_file"
         mv "$file" "$new_file"
      
    fi
done

# Change back to the original directory
cd "$current_directory"

