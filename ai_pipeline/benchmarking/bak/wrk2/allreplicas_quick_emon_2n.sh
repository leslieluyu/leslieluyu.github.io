
FRONTEND=${1:-"10.0.1.37"}
OVERRIDE=${2:-"override.yaml"}
WRKDIR=$(cd $(dirname "$0") && pwd)
SVRINFO="/tmp/svrinfo"
TS="`date "+%Y%m%d%H%M%S"`"
echo "TS=$TS"
#prepare for the requirements
./looptest_pre.sh
NS1="gms-ctl0"
NS2="gms-ctl1"
# Loop for replicas
for replica in  30 
do
# Create the directory
#TT=clxvm24r${replica}
TT="gmsdata_${TS}_${replica}"
echo "Run on test $TT"
echo "TT=$TT"
mkdir -p  ~/${TT}
# pre delete helm
$WRKDIR/../helm/helmdelete.sh ${NS1}
$WRKDIR/../helm/helmdelete.sh ${NS2}
$WRKDIR/../helm/helmdelete.sh
# Save the svrinfo
cd $WRKDIR
mkdir -p $SVRINFO
svr_info --targets ./targets --out $SVRINFO
mv -f "$SVRINFO" ~/${TT}/
# Loop for rounds
# for loop in first
for loop in 1
do
  echo $loop
  mkdir -p ~/${TT}/round${loop}
  cd ${WRKDIR}/../helm
  ./helminstall.sh ${replica} ${NS1} ${OVERRIDE} &
  ./helminstall.sh ${replica} ${NS2} ${OVERRIDE}
  sleep 30
  PORT1=`kubectl get svc -n ${NS1} |grep frontend-external |awk -F ":" '{print $2}' |awk -F "/" '{print $1}'`
  PORT2=`kubectl get svc -n ${NS2} |grep frontend-external |awk -F ":" '{print $2}' |awk -F "/" '{print $1}'`
  kubectl get pods -A -owide > ~/${TT}/round${loop}/podpretest.txt
  cd ${WRKDIR}
  ./looptest_emon_2ns.sh ${FRONTEND}:${PORT1} ${FRONTEND}:${PORT2} 27000 30000
  sudo mv result ~/${TT}/round${loop}/
  sudo mv emon* ~/${TT}/round${loop}/
  #sudo mv serverinfo ~/${TT}/round${loop}/
  kubectl get pods -A -owide > ~/${TT}/round${loop}/podposttest.txt
  cd ${WRKDIR}/../helm
  ./helmdelete.sh ${NS1}
  ./helmdelete.sh ${NS2}
  sleep 350
# Loop for rounds
done
# Loop for replicas
done
