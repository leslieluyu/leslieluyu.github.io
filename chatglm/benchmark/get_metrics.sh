#!/bin/bash
LOG_PATH=${1:-"~/metrics_log"}
LOG_FILE=${2:-"20230911_CPU16_R1_metrics"}
PID=${3:-"12008"}


# 1. init the env
mkdir -p ${LOG_PATH}

# 2. cpu usage by pid
# 2.1  get PID
# 2.2  get CPU and write to log

# 3. get memory bandwidth perf

