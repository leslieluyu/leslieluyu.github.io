bash
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

# Loop through the array and tag each image
for image in "${images[@]}"
do
    # Extract the image name and tag
    image_name=$(echo "$image" | cut -d'/' -f2)
    image_tag=$(echo "$image" | cut -d':' -f2)

    # Construct the new image name with the 'oper' repository
    new_image="opea/$image_name:$image_tag"

    echo "Tagging $image as $new_image"
    docker tag "$image" "$new_image"
done
