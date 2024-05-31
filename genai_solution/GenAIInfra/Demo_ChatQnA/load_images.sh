#!/bin/bash

# Array of images
images=(
  "opea/chatqna-ui:latest"
  "opea/chatqna:latest"
  "opea/tei-gaudi:latest"
  "opea/dataprep-redis:latest"
  "opea/llm-tgi:latest"
  "opea/reranking-tei:latest"
  "opea/retriever-redis:latest"
  "opea/embedding-tei:latest"
)

# Export each image to a separate tar file
for image in "${images[@]}"; do
  tar_file="${image//\//}.tar"
  docker save -o "$tar_file" "$image"
done

# Load images from the tar files
for tar_file in *.tar; do
  sudo nerdctl -n k8s.io load -i "$tar_file"
done

# Clean up tar files
#rm *.tar

