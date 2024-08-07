#!/bin/bash

# Array of YAML file names
yaml_files=("qna_configmap_mixed" "redis-vector-db"  "tei_embedding_service" "tei_reranking_service" "tgi_gaudi_service" "retriever" "embedding" "reranking" "llm" "chaqna-xeon-backend-server")
for element in ${yaml_files[@]}
do
    echo "Delete manifest from ${element}.yaml"
    kubectl delete -f "${element}.yaml"
done
