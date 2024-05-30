pod_name=${1:-""}
namespace=${2:-""}
pid=${3:-""}
# pod_uid=${1:-""}
# container_id=${2:-""}
echo "pod_name=${pod_name} namespace=${namespace}"

pod_uid=`kubectl  get pod $pod_name -n $namespace -o jsonpath='{.metadata.uid}' | sed -e s/-/_/g`
echo "UID of $pod_name is $pod_uid"
container_id=`kubectl  get pod $pod_name -n $namespace -o jsonpath='{.status.containerStatuses[0].containerID}' | cut -d "/" -f 3`
echo "container id is $container_id"
container_fs=`find /sys/fs/cgroup -name "*${container_id}*"`
cmdline='cat $(find /sys/fs/cgroup/ -name "'"*${container_id}*"'")/cgroup.threads'
#cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.threads"
echo "cmdline=${cmdline}"

# mkdir in rdt by pid
ansible -i hosts job -m shell -a "mkdir /sys/fs/resctrl/cri-resmgr.high/mon_groups/{{pid}}" -e "pid='$pid'" --become --become-method=sudo
# enable all the pid&threading in top tasks
ansible -i hosts job -m shell -a "threads=\$( {{ cmd }} ); for t in \$threads; do echo \"t=\$t\"; echo \$t > /sys/fs/resctrl/cri-resmgr.high/tasks; done" -e "cmd='$cmdline'" --become --become-method=sudo
# enable all the pid&threading in pid tasks
ansible -i hosts job -m shell -a "threads=\$( {{ cmd }} ); for t in \$threads; do echo \"t=\$t\"; echo \$t > /sys/fs/resctrl/cri-resmgr.high/mon_groups/{{pid}}/tasks; done" -e "cmd='$cmdline'" -e "pid='$pid'" --become --become-method=sudo




 

echo "done"
