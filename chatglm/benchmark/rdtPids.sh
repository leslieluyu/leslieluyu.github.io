flag_cpum=${1:-0}
# for gurantee
namespace=default
pods=`kubectl  get pod -n $namespace |grep llm | cut -d " " -f1`
for pod in $pods
do
        pod_uid=`kubectl  get pod $pod -n $namespace -o jsonpath='{.metadata.uid}' | sed -e s/-/_/g`
        echo "UID of $pod is $pod_uid"
        container_id=`kubectl  get pod $pod -n $namespace -o jsonpath='{.status.containerStatuses[0].containerID}' | cut -d "/" -f 3`
        echo "container id is $container_id"
	#cpu spr
	#cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.threads"
        if [ $flag_cpum -eq 1 ]; then
            cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.threads"
        else
            cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.threads"
        fi
        #threads=`cat /sys/fs/cgroup/cpu,cpuacct/kubepods.slice/kubepods-besteffort.slice/kubepods-besteffort-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.procs`
	echo "cmdline=${cmdline}"
	#ansible -i hosts llm -m shell -a "threads={{cmd}};for t in $threads; do echo "t=$t"; echo $t > /sys/fs/resctrl/cri-resmgr.high/tasks; done" -e "cmd='$cmdline'" --become --become-method=sudo
	ansible -i hosts job -m shell -a "threads=\$( {{ cmd }} ); for t in \$threads; do echo \"t=\$t\"; echo \$t > /sys/fs/resctrl/cri-resmgr.high/tasks; done" -e "cmd='$cmdline'" --become --become-method=sudo


#        ansible -i hosts llm -m shell -a "{{cmd}}" -e "cmd='$cmdline'"	
	#threads=$(ansible -i hosts llm -m shell -a "{{cmd}}" -e "cmd='$cmdline'")
#	ansible -i hosts llm -m shell -a "cat /sys/fs/cgroup/cpu"
        #echo "threads=$threads" 
        #echo "adding threads to control group"
        #for t in $threads; do echo $t > /sys/fs/resctrl/cri-resmgr.high/tasks; done
        #echo ""
done

 

echo "done"
