
LLM_PID=./llm.pid
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
	#for cpumanager in skylake cmdline="cat /sys/fs/cgroup/cpu,cpuacct/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/tasks"
	#for cpumanager in spr cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.procs"
	#for nocpumanager in skylake cmdline="cat /sys/fs/cgroup/cpu,cpuacct/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/tasks"
	
        if [ $flag_cpum -eq 1 ]; then
            cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.procs"
        else
            cmdline="cat /sys/fs/cgroup/kubepods.slice/kubepods-pod$pod_uid.slice/cri-containerd-$container_id.scope/cgroup.procs" # for nocpumanager in spr
        fi
        echo "cmdline=${cmdline}"
	#ansible -i hosts llm -m shell -a "threads={{cmd}};for t in $threads; do echo "t=$t"; echo $t > /sys/fs/resctrl/cri-resmgr.high/tasks; done" -e "cmd='$cmdline'" --become --become-method=sudo
	#ansible -i hosts job -m shell -a "threads=\$( {{ cmd }} ); for t in \$threads; do echo \"t=\$t\"; echo \$t > /sys/fs/resctrl/cri-resmgr.high/tasks; done" -e "cmd='$cmdline'" --become --become-method=sudo
        #ansible -i hosts job -m shell -a "date"
        llm_pid=`ansible-playbook -i hosts metric_jobs.yaml --tags get_pid,output_jobid  --extra-vars "cmd='$cmdline'" | grep msg|awk -F'"' '/msg/ {print $4}'`
        #ansible -i hosts job -m debug -a "var=ret_str"
        #threads_value=$(ansible -i hosts job -m debug -a "var=ret_str" | awk -F'|' 'NR==2 {print $NF}' | tr -d ' ')
        echo "llm_pid=$llm_pid" 
        echo $llm_pid > $LLM_PID
done

 

echo "done"
echo "llm_pid:$llm_pid"
exit 0


#!/bin/bash

# Run the Ansible playbook
ansible_output=$(ansible -i hosts job -m shell -a "threads=\$(date)" 2>&1)

# Check the return code of the Ansible command
if [ $? -eq 0 ]; then
    echo "Ansible command executed successfully"
    
    # Extract the 'threads' variable from the Ansible output
    threads_value=$(echo "$ansible_output" | grep -oP 'threads=\K.*')
    
    # Print the value of the 'threads' variable
    echo "The 'threads' variable value is: $threads_value"
else
    echo "Ansible command failed"
fi
exit 0


