HOSTS=${1:-"./hosts"}
ansible -i ${HOSTS} emon -m copy -a 'src=cpu_manager.sh dest=~/ mode=755'
ansible -i ${HOSTS} emon -m shell -a 'sudo ~/cpu_manager.sh disable'
sleep 8
ansible -i ${HOSTS} emon -m shell -a 'sudo cat  /var/lib/kubelet/cpu_manager_state'
