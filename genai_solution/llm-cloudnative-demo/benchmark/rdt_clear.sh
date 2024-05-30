

RDT_MON_GROUP="/sys/fs/resctrl/cri-resmgr.high/mon_groups"

# clear paths in rdt_path by pid
echo "will delete all the mon groups in RDT"
ansible -i hosts job -m shell -a "ls {{ rdt_mon_group }}" -e "rdt_mon_group='$RDT_MON_GROUP'" --become --become-method=sudo
echo "Now delete ..."
ansible -i hosts job -m shell -a "cd {{ rdt_mon_group }};ls;ls |xargs -I {} sudo rmdir {}" -e "rdt_mon_group='$RDT_MON_GROUP'" --become --become-method=sudo

echo "done"
