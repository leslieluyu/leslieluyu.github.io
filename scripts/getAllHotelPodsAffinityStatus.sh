#!/bin/bash  
NS_P=hotel-res
CMD_PODINFO='kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NS:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase'
FILENAME='/tmp/hotel.pod.info'
for i in {0..3}  
do  
  #echo $(expr $i \* 3 + 1);  
  NS=${NS_P}${i}
  echo "NS=${NS}"
#  for pod in `kubectl get pod -n ${NS}|awk '{print $1}'`
  ${CMD_PODINFO} -n ${NS}|sort|awk 'NR>2{print line}{line=$0} END{print line}' > $FILENAME
  while read -r line
  do
    echo $line
    arr=($line)
    #echo ${line[@]} ${arr[0]}
    node=${arr[0]}
    ns=${arr[1]}
    pod=${arr[2]}
    echo "node=${node},ns=${ns},NS=${NS}, pod=${pod}"
    kubectl exec -n ${NS}  -ti ${pod}  -- /bin/sh -c "cat /proc/self/status"|grep allowed_list

  done < ${FILENAME}
  
#for line in $(cat $FILENAME)
#  do
#    echo "LINE=${line}"
    #echo "POD=${pod}"
#  done
done 
