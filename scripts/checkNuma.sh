
FILENAME='/tmp/hotel.pod.info'
kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NS:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase -A|grep  'hotel-res'|sort > $FILENAME
  #while read -r line
  O_IFS=$IFS
  IFS=$'\n'
  for line in `cat $FILENAME`
  do
    echo $line
    IFS=$O_IFS
    arr=($line)
    #echo ${line[@]} ${arr[0]}
    node=${arr[0]}
    ns=${arr[1]}
    pod=${arr[2]}
    echo "node=${node},ns=${ns},NS=${NS}, pod=${pod}"
    kubectl exec -n ${ns}  -ti ${pod}  -- /bin/sh -c "cat /proc/self/status"|grep allowed_list
  done
  #done < ${FILENAME}
