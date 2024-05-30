#Mount and create a RDT Group 

sudo mount -t resctrl resctrl /sys/fs/resctrl 
sudo mkdir /sys/fs/resctrl/cri-resmgr.high
