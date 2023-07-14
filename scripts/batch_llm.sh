#!/bin/bash
dt=`TZ='Asia/Shanghai' date "+%m%d%H%M%S"`
python3 /home/ansible/yulu/leslieluyu.github.io/scripts/batch_llm.py 2>&1|tee batch_llm_all_${dt}.log