
# Examples running wrk in container
SERVER=${1:-"10.233.8.155"}
RPS=${2:-2000}
TIMETAG=${3:-"yymmddhhmmss"}
echo "Testing on $SERVER with $RPS Requests per second"
RESULTDIR=/client/result/rps${RPS}
mkdir -p ${RESULTDIR}

wrk -t 20 -c1600 -d60s -R${RPS} --latency -s /client/mixed-workload.lua http://${SERVER} \
  |tee -a ${RESULTDIR}/wrklog.${TIMETAG}


