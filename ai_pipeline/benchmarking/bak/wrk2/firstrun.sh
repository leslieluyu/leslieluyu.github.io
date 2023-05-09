
FRONTEND=${1:-"10.0.1.37"}
WRKDIR=$(cd $(dirname "$0") && pwd)
# Create the directory
#kubectl create ns test
#TT=clxvm24firstrun
TT=tttfirstrun
echo "Run on test $TT"
mkdir ~/${TT}
ansible -i hosts emon -m shell -a "sudo apt install -y sysstat"
# Save the svrinfo
#mkdir svrinfo
#svr_info --targets ./targets --out svrinfo
#mv svrinfo ~/${TT}/
for loop in first
do
  echo $loop
  mkdir ~/${TT}/round${loop}
  cd ${WRKDIR}/../helm
  ./helminstall.sh 50
  sleep 30
  PORT=`kubectl get svc |grep frontend-external |awk -F ":" '{print $2}' |awk -F "/" '{print $1}'`
  kubectl get pods -owide > ~/${TT}/round${loop}/podpretest.txt
  cd ${WRKDIR}
  ./looptest.sh ${FRONTEND}:${PORT} 5000 35000
  sudo mv result ~/${TT}/round${loop}/
  sudo mv emon* ~/${TT}/round${loop}/
  #sudo mv serverinfo ~/${TT}/round${loop}/
  kubectl get pods -owide > ~/${TT}/round${loop}/podposttest.txt
  cd ${WRKDIR}/../helm
  ./helmdelete.sh
  sleep 350
done
