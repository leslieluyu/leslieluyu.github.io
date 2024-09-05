#! /bin/bash
# a.sh
podname=$1
cgroupdir="/sys/fs/cgroup/kubepods.slice/"
#crictl ps -name $podname -v  | grep -A1 "ID" | while read -r id podid podname reset;do
#crictl ps  --name $podname | while read -r container image created state name reset;do
sudo crictl ps |grep $podname | while read -r a b c d e f g h;do
   #echo $a
   echo "pod $g"
   dir=`find $cgroupdir -name *$a*`
   #echo $dir/cpuset.cpus
   cpus=`cat $dir/cpuset.cpus`
   echo "cpus $cpus"
done
