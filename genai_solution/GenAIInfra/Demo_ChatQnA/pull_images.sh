#!/bin/bash

# Array of Docker images
images=(
    "docker201904/tei-gaudi:latest"
    "docker201904/chatqna:latest"
    "docker201904/embedding-tei:latest"
    "docker201904/reranking-tei:latest"
    "docker201904/retriever-redis:latest"
    "docker201904/llm-tgi:latest"
)

# Loop through the array and pull each image
for image in "${images[@]}"
do
    echo "Pulling image: $image"
    docker pull "$image"
done
