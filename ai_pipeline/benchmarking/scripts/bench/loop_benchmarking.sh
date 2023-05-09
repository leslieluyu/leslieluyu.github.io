#!/bin/bash

scenario=${1:-AMX_BF16}
round=${2:-3}
metrics_path="metrics"
WRKDIR=$(cd $(dirname "$0") && pwd)
SVRINFO="/tmp/svrinfo"
TS="`date "+%Y%m%d%H%M%S"`"
echo "TS=$TS"

#prepare for the requirements
./looptest_pre.sh

# Loop for replicas
for replica in  6 
do
  # Create the directory
  TT="AiPipeline_${TS}_${scenario}_${replica}"
  echo "Run on test $TT"
  echo "TT=$TT,WRKDIR=${WRKDIR}"
  mkdir -p  ~/${TT}
  # pre delete last current deploy TODO
  
  # Save the svrinfo
  cd $WRKDIR
  #mkdir -p $SVRINFO
  #svr_info --targets ./targets --out $SVRINFO
  #mv -f "$SVRINFO" ~/${TT}/
  # Loop for rounds
  for loop in $(seq 1 ${round})
  do
    echo "-----------loop num:${loop}/${round}------------"
    mkdir -p ~/${TT}/round${loop}
    sleep 10
    cd ${WRKDIR}
    # 1. fetch the emon
    echo "1.  fetch_emon.sh" 
    echo "pwd=$(pwd)"
    ./fetch_emon.sh 
    # 2. fetch the matrics of ai_pipeline TODO
    # fetch the matrics into the result folder
    echo "2. fetch the matrics of ai_pipeline" 
    
    
    # 3. collect the result
    echo "3.  collect the result"
    mkdir -p "${metrics_path}"

    python3 fetch_metrics.py -s ${scenario} -P ${metrics_path}

    sudo mv metrics ~/${TT}/round${loop}/
    sudo mv emon* ~/${TT}/round${loop}/
    if [ ${loop} -ne ${round} ]; then
      echo "sleep 120 seconds for the next round ..."
      sleep 120
    fi
  # Loop for rounds
  done
# Loop for replicas
done
