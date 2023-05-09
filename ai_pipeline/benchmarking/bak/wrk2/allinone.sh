
FRONTEND=${1:-"10.0.1.77"}
# Save the svrinfo
#mkdir svrinfo
#svr_info --targets ./targets --out svrinfo
#mv svrinfo ~/clxvm12/
for loop in 1 2 3
do
  echo $loop
  cd ~/GoogleMicroserviceDemo/helm
  ./helminstall.sh
  sleep 30
  PORT=`kubectl -n test get svc |grep frontend-external |awk -F ":" '{print $2}' |awk -F "/" '{print $1}'`
  kubectl -n test get pods -owide > ~/clxvm12/round${loop}/podpretest.txt
  cd ~/GoogleMicroserviceDemo/wrk2
  ./armtest.sh ${FRONTEND}:${PORT}
  sudo mv result ~/clxvm12/round${loop}/
  kubectl -n test get pods -owide > ~/clxvm12/round${loop}/podposttest.txt
  cd ~/GoogleMicroserviceDemo/helm
  ./helmdelete.sh
  sleep 350
done
