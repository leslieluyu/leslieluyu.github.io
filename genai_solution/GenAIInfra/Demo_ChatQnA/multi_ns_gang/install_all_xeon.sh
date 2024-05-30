#!/bin/bash

############################################################
# Help                                                     #
############################################################
function usage()
{
   ME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
   echo "Deployment script of ChatQnA workload."
   echo
   echo "Syntax:  $ME <replica> [-n|-h]"
   echo "options:"
   echo "-n <name>   Optional, specify a different namespace."
   echo "-i <number> Optional, specify replica count."
   echo "-h          Print this Help."
   echo
   echo example: $ME -i 3 -n chatQnA
   echo
   exit 0
}

############################################################
# Process the input options. Add options as needed.        #
############################################################
# Get the options
while :; do
  while getopts ":hin:" option; do
     case $option in
        h) # display Help
           usage
           exit;;
        n) # Enter a namespace
           K8S_NS=$OPTARG;;
        i) # Enter a namespace
           replica=$OPTARG;;
       \?) # Invalid option
           echo "Error: Invalid option"
           usage
           exit;;
     esac
  done
((OPTIND++))
[ $OPTIND -gt $# ] && break
done

[ "x$replica" == "x" ] && replica=1

if [ "$replica" -gt 0 ] 2>/dev/null ;then
  echo "OK"
else
  usage
fi


[ "x$K8S_NS" == "x" ] && K8S_NS="chatqna"

export K8S_NS=$K8S_NS

kubectl create namespace ${K8S_NS}

# Array of YAML file names
yaml_files=("qna_configmap_xeon" "redis-vector-db"  "tei_embedding_service" "tei_reranking_service" "tgi_service" "retriever" "embedding" "reranking" "llm" "chaqna-xeon-backend-server")
for element in ${yaml_files[@]}
do
    echo "Applying manifest from ${element}.yaml"
    cat "${element}.yaml" |envsubst|kubectl apply -f- -n $K8S_NS
done
