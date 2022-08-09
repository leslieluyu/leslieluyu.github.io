#!/bin/bash

TOPDIR=`pwd`/
OUTPUT=/tmp/perfkitbenchmarker

SVR_INFO_PKG=/home/yangfen1/go/src/MicroservicesWorkloadsRelease/infra/CodeBase/cloud.benchmarking.deployment/k8s/internal_tools/svr_info_internal_1.4.0.tgz
GMS_SOURCE_PKG=/home/yangfen1/go/src/MicroservicesWorkloadsRelease/googleMicroServices/CodeBase/gms_rc2.tar.gz
EMON_PKG=/home/yangfen1/go/src/MicroservicesWorkloadsRelease/infra/CodeBase/cloud.benchmarking.deployment/k8s/internal_tools/sep_private_5_30_linux_111018263d8165d.tar.bz2
#DOCKER_REGISTRY_URL=172.16.27.100:5000/
#DOCKER_IMAGE_TAG=rc2
#NAMESPACE=gms
WRK_THREADS=20
WRK_CONNECTIONS=1600
WRK_INIT_WRK_RATE=40000
WRK_RATE_INC=2500

CLUSTER=$1
CONFIG=$2

function usage() {
    echo "$0 <cluster type> <config_file>"
    exit 1
}

[ "x$CLUSTER" == "x" ] && usage
[ ! -f "$CONFIG" ] && usage

if [ -d $OUTPUT ]; then
    echo "remove $OUTPUT"
    rm $OUTPUT -rf
fi
mkdir $OUTPUT

if [ ! -f venv/bin/activate ]; then
    virtualenv -p python3 venv
    source venv/bin/activate
else
    source venv/bin/activate
fi
pip install -r $TOPDIR/requirements.txt

#REPLICAS=(40 50 60 70 80)
REPLICAS=(1)

for r in ${REPLICAS[@]}; do
    echo "Running replica $r for cluster $CLUSTER of config $CONFIG ..."
    runuri="r${r}${CLUSTER}"
    runuri=${runuri:0:12}

    $TOPDIR/pkb.py \
        --temp_dir=${OUTPUT} \
        --benchmarks=intel_gms \
        --benchmark_config_file=${CONFIG} \
        --svrinfo=true \
        --svrinfo_tarball=${SVR_INFO_PKG} \
	--gms_tarball_archive_url=${GMS_SOURCE_PKG} \
	--run_uri=$runuri \
        --replica_count=$r \
	--gms_wrk_init_rate=${WRK_INIT_WRK_RATE} \
	--gms_wrk_rate_increment=${WRK_RATE_INC} \
#        --intel_gms_images_registry=${DOCKER_REGISTRY_URL} \
#        --intel_gms_images_tag=${DOCKER_IMAGE_TAG} \
#	--intel_gms_namespace=${NAMESPACE} \
#	--gms_namespace_count=2 \
#	--intel_gms_container_runtime_cli="sudo nerdctl" \
#        --trace_vm_groups=worker 
#        --emon \
#        --emon_tarball=${DSB_EMON_PKG} \
#        --emon_post_process_skip \
#        --trace_allow_benchmark_control
done


