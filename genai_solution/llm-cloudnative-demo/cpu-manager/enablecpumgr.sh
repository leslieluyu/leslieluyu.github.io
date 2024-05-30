HOSTS=${1:-"./hosts"}
str="To enable the cpu manager on a node:\n \
1. Add entries to /etc/Kubernetes/kubelet-config.yaml\n \
systemReserved:\n \
  cpu: 500m\n \
  memory: 256Mi\n \
kubeReserved:\n \
  cpu: 500m\n \
  memory: 256Mi\n \
cpuManagerPolicy: static\n \
\n\
2. Edit /etc/systemd/system/kubelet.service.d/10-kubeadm.conf\n \
to use the above config file\n \
Environment=\"KUBELET_CONFIG_ARGS=--config=/etc/kubernetes/kubelet-config.yaml\“\n \
 \n\
3. Remove /var/lib/kubelet/cpu_manager_state\n \
rm /var/lib/kubelet/cpu_manager_state\n \
 \n\
4. Restart kubelet service\n \
systemctl restart kubelet\n \
\n \
5. Check cpu manager enabled\n \
cat /var/lib/kubelet/cpu_manager_state\n \
"

#echo $str
ansible -i ${HOSTS} emon -m copy -a 'src=cpu_manager.sh dest=~/ mode=755'
ansible -i ${HOSTS} emon -m shell -a 'sudo ~/cpu_manager.sh enable'
sleep 8
ansible -i ${HOSTS} emon -m shell -a 'sudo cat  /var/lib/kubelet/cpu_manager_state'
