
# import the wrk2 client docker images before run
CURDIR=`pwd`
LOCALREG=${1:-"10.0.1.47:5000"}
. base.sh
docker run --name wrk2 --ulimit nofile=102400:102400 -d -v ${CURDIR}:/client ${LOCALREG}/wrk-client:baseline sleep infinity
docker exec wrk2 cp wrk /usr/bin/
