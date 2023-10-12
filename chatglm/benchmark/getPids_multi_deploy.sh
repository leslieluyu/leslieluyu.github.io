
pod_name=${1:-""}
namespace=${2:-""}
# pod_uid=${1:-""}
# container_id=${2:-""}
echo "pod_name=${pod_name} namespace=${namespace}"

pod_uid=`kubectl  get pod $pod_name -n $namespace -o jsonpath='{.metadata.uid}' | sed -e s/-/_/g`
echo "UID of $pod_name is $pod_uid"
container_id=`kubectl  get pod $pod_name -n $namespace -o jsonpath='{.status.containerStatuses[0].containerID}' | cut -d "/" -f 3`
echo "container id is $container_id"
cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.procs"
echo "cmdline=${cmdline}"
llm_pid=`ansible-playbook -i hosts metric_jobs.yaml --tags get_pid,output_jobid  --extra-vars "cmd='$cmdline'" | grep msg|awk -F'"' '/msg/ {print $4}'`
echo "llm_pid=$llm_pid" 



