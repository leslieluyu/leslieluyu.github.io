
FRONTEND=${1:-"10.0.1.37"}
NS=${2:-"gms"}
OVERRIDE=${3:-"override.yaml"}
WRKDIR=$(cd $(dirname "$0") && pwd)
SVRINFO="/tmp/svrinfo"
TS="`date "+%Y%m%d%H%M%S"`"
echo "TS=$TS"
#prepare for the requirements
./looptest_pre.sh

# Loop for replicas
for replica in  60 
do
# Create the directory
#TT=clxvm24r${replica}
TT="gmsdata_${TS}_${replica}"
echo "Run on test $TT"
echo "TT=$TT"
mkdir -p  ~/${TT}
# pre delete helm
$WRKDIR/../helm/helmdelete.sh
# Save the svrinfo
cd $WRKDIR
mkdir -p $SVRINFO
svr_info --targets ./targets --out $SVRINFO
mv -f "$SVRINFO" ~/${TT}/
# Loop for rounds
for loop in 1 2 3
do
  echo $loop
  mkdir -p ~/${TT}/round${loop}
  cd ${WRKDIR}/../helm
  ./helminstall.sh ${replica} ${NS} ${OVERRIDE} 
  sleep 30
  PORT=`kubectl get svc -n ${NS}|grep frontend-external |awk -F ":" '{print $2}' |awk -F "/" '{print $1}'`
  kubectl get pods -n ${NS} -owide > ~/${TT}/round${loop}/podpretest.txt
  cd ${WRKDIR}
  ./looptest_emon.sh ${FRONTEND}:${PORT} 54000 60000
  sudo mv result ~/${TT}/round${loop}/
  sudo mv emon* ~/${TT}/round${loop}/
  #sudo mv serverinfo ~/${TT}/round${loop}/
  kubectl get pods -n ${NS} -owide > ~/${TT}/round${loop}/podposttest.txt
  cd ${WRKDIR}/../helm
  ./helmdelete.sh ${NS}
  sleep 350
# Loop for rounds
done
# Loop for replicas
done
