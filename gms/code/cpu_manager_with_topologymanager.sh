#! /bin/bash

CONF="/var/lib/kubelet/config.yaml"
BACKUP_CONF="${CONF}.bak"
STATE_FILE="/var/lib/kubelet/cpu_manager_state"
KEY="cpuManagerPolicy: static"
echo "BACKUP_CONF=$BACKUP_CONF"
function usage(){
    echo "Usage: `basename $0` disable|enable"
}

function enable_cpu_manager(){
  echo "... in enable_cpu_manager() "
  # if the file not exists then backup first /var/lib/kubelet/config.yaml
  if [ ! -f "$BACKUP_CONF" ]; then
    echo "... make the backup : $BACKUP_CONF "
    cp $CONF $BACKUP_CONF
  else
    echo "... the backup config file is already exists."	
  fi
  # add cpu_policy
  if [ `grep -c "$KEY" $CONF` -eq '0' ];then
  cat >> "${CONF}" <<EOF
cpuManagerPolicy: static
systemReserved:
  cpu: 500m
  memory: 256Mi
kubeReserved:
  cpu: 500m
  memory: 256Mi
topologyManagerPolicy: best-effort
EOF
    echo "... add cpuManagerPolicy to $CONF"
  else
    echo "... cpuManagerPolicy is already exist in $CONF"
  fi
  # remove cpu_manager_state
  #mv -b $STATE_FILE /tmp/$STATE_FILE
  rm $STATE_FILE -f
  echo "... remove $STATE_FILE" 
  # restart kubelet
  systemctl daemon-reload
  systemctl reload-or-restart kubelet
  echo "... restart kubelet.service"
  # check cpu manager status
  #cat $STATE_FILE
  echo "please check the cpu manager status. policyName should be static"
}

function disable_cpu_manager(){
  echo "... in disable_cpu_manager() "
  # 1. restore backup config 
  if [  -f "$BACKUP_CONF" ]; then
    echo "... restore the backup:$BACKUP_CONF to $CONF "
    cp -f $BACKUP_CONF $CONF
  else
    echo "... the backup config file is not exists. Exiting ..."
    exit 55
  fi
  # 2. remove cpu_manager_state
  rm $STATE_FILE -f
  echo "... remove $STATE_FILE"
  # 3. restart kubelet
  systemctl daemon-reload
  systemctl reload-or-restart kubelet
  echo "... restart kubelet.service"
  # 4. check cpu manager status
  echo "please check the cpu manager status.  policyName should be empty"
}

case "$1" in
    -h|--help|?)
    usage
    exit 55
;;
    enable|disable)
    if [ "$1" == "enable" ] ; then
      echo "... enable cpu manager"
      # something
      enable_cpu_manager
      exit
    elif [ "$1" == "disable" ] ; then
      echo "... disable cpu manager"
      # something
      disable_cpu_manager
      exit
    fi
;;
    *)
      echo "the arg is not correct!"
      usage
      exit 55
;;
esac

if [ ! -n "$1" ] ; then
    usage
    exit 55
fi

