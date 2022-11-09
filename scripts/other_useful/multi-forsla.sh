RETRIES=(1 2 3 4 5 6 7 8 9 10 11)
RPSS=(27500 28000 28500)
RUNS=("sla275" "sla280" "sla285")
i=1
#for rps in ${RPSS[@]}; do
for ((i=0;i<${#RPSS[@]};i++))
do
  echo "RPS=${RPSS[$i]}"
  for r in ${RETRIES[@]}; do
    echo "r=${r} runs=${RUNS[$i]}"
    echo "Running retries of  $r  ..."
    ./pkb.py --benchmarks=dsbpp_hotel \
            --benchmark_config_file=perfkitbenchmarker/data/dsbpp_hotel/dsbpp_hotel_static.yaml \
            --dsbpp_hotel_replicas_override=6 \
            --dsbpp_hotel_client_instances_per_vm=1 \
            --dsbpp_hotel_client_threads=32 \
            --dsbpp_hotel_client_connections=1920 \
            --dsbpp_hotel_client_duration=120 \
            --dsbpp_hotel_client_rate=${RPSS[$i]} \
            --dsbpp_hotel_gcpercent=1000 \
            --dsbpp_hotel_memctimeout=500 \
            --dsbpp_hotel_namespace_count=4 \
            --dsbpp_hotel_enable_crirm \
            --k8s_get_retry_count=300 \
            --emon \
            --emon_tarball=../infra/k8s/internal_tools/sep_private_5_34_linux_050122015feb2b5.tar.bz2 \
            --trace_vm_groups=worker \
            --svrinfo=False \
            --dsbpp_hotel_client_timeout=20 \
            --run_uri=${RUNS[$i]}r$r
   
  done

done
#done
