
SERVER=$1
RPS=2000
WARMUPCMD="wrk -t 8 -c400 -d30s -R${RPS} --latency -s /client/mixed-workload.lua http://${SERVER}"
for i in `seq 1 100`
do
	$WARMUPCMD
done
