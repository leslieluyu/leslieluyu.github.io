#!/bin/bash

count_urls=()
total_count=0

# Loop through each JSON file in the current directory
for file in *.json; do
  if [ -f "$file" ]; then
    # Use jq to extract all 'source_url' values into an array
    urls=$(jq -c '.[].source_url' "$file")

    # Loop through each extracted URL
    while IFS= read -r url; do
      found=false
      # Check if the URL is already in our count array
      for i in "${!count_urls[@]}"; do
        if [[ "${count_urls[$i]}" == "$url:*" ]]; then
          # Increment the count if found
          count=$(echo "${count_urls[$i]}" | cut -d':' -f2)
          count=$((count + 1))
          count_urls[$i]="$url:$count"
          found=true
          break
        fi
      done
      # Add the URL with a count of 1 if not found
      if [ "$found" = false ]; then
        count_urls+=("$url:1")
      fi
      # Increment the total count for each URL found
      total_count=$((total_count + 1))
    done <<< "$urls"
  fi
done

# Print the counts of each source_url
echo "Source URL Counts:"
for item in "${count_urls[@]}"; do
  echo "$item"
done

# Print the total count
echo "\nTotal Count of 'source_url' across all files: $total_count"
