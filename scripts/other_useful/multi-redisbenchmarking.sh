RUNS=${1}
RETRIES=(1 2 3 4 5 6 7 8 9 10 11)
i=1
  for r in ${RETRIES[@]}; do
    echo "r=${r} runs=${RUNS}"
    echo "Running retries of  $r  ..."
    redis-benchmark -h 127.0.0.1 -p 30778 -c 120  -q|tee redis${r}-${RUNS}.log 
  done

