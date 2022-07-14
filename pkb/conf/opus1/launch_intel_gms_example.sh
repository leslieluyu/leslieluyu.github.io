#!/bin/bash

TOPDIR=`pwd`/../../..
OUTPUT=/tmp/perfkitbenchmarker
SVR_INFO_PKG=/home/ansible/yulu/MicroservicesWorkloadsRelease/infra/CodeBase/cloud.benchmarking.deployment/k8s/internal_tools/svr-info-internal-2.0.2.tgz
GMS_SOURCE_PKG=/home/ansible/yulu/gms.rc2.tar.gz
EMON_PKG=/home/ansible/yulu/MicroservicesWorkloadsRelease/infra/CodeBase/cloud.benchmarking.deployment/k8s/internal_tools/sep_private_5_34_linux_050122015feb2b5.tar.bz2
DOCKER_REGISTRY_URL=10.250.18.9:5000/
DOCKER_IMAGE_TAG=rc2
NAMESPACE=gms
WRK_THREADS=20
WRK_CONNECTIONS=1600
WRK_INIT_WRK_RATE=48000
WRK_RATE_INC=1000

CLUSTER=$1
CONFIG=$2

function usage() {
    echo "$0 <cluster type> <config_file>"
    exit 1
}

[ "x$CLUSTER" == "x" ] && usage
[ ! -f "$CONFIG" ] && usage

#if [ -d $OUTPUT ]; then
#    echo "remove $OUTPUT"
#    rm $OUTPUT -rf
#fi
mkdir $OUTPUT

if [ ! -f venv/bin/activate ]; then
    virtualenv -p python3 venv
    source venv/bin/activate
else
    source venv/bin/activate
fi
pip install -r $TOPDIR/requirements.txt

#REPLICAS=(40 50 60)
REPLICAS=(60 )
for r in ${REPLICAS[@]}; do
    echo "Running replica $r for cluster $CLUSTER of config $CONFIG ..."
    runuri="r${r}${CLUSTER}"
    runuri=${runuri:0:12}

    $TOPDIR/pkb.py \
        --temp_dir=${OUTPUT} \
        --benchmarks=intel_gms \
        --benchmark_config_file=${CONFIG} \
        --svrinfo=True \
	--svrinfo_tarball=${SVR_INFO_PKG} \
        --gms_tarball_archive_url=${GMS_SOURCE_PKG} \
        --run_uri=$runuri \
        --replica_count=$r \
	--gms_wrk_threads=${WRK_THREADS} \
        --gms_client_connections=${WRK_CONNECTIONS} \
        --gms_wrk_init_rate=${WRK_INIT_WRK_RATE} \
        --gms_wrk_rate_increment=${WRK_RATE_INC} \
        --gms_images_registry=${DOCKER_REGISTRY_URL} \
        --gms_images_tag=${DOCKER_IMAGE_TAG} \
        --gms_namespace=${NAMESPACE} \
	--gms_namespace_count=1 \
	--gms_container_runtime_cli="sudo nerdctl" \
	--trace_vm_groups=worker \
        --emon \
        --emon_tarball=${EMON_PKG} \
        --emon_post_process_skip \
        --trace_allow_benchmark_control
done

