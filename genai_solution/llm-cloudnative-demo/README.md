# Guide for Deploy  llm-cloudnative-demo 
## 1. Overview
The purpose of this demo is to achieve an easily deployable, scalable, and monitorable end-to-end GenAI workload running in a cloud-native environment. 

It includes the following components:
- LLM-inference-Service Containers running on Kubernetes Cluster
- Gateway to load balance the requests
- Traffic Generator to simulate the requests
- Metric Endpoints
- Prometheus&Grafana to collect and visualization the key metrics

### GenAI Workload Architecture

![Gen-AI-Soultion-123-240124](https://github.com/intel-sandbox/cloud.performance.workload.generative-ai.llm/assets/5109898/ff5db6c5-9963-4712-8e22-8521451e9152)

Target:
- A containerized Cloud native generative AI large language models(LLM) workload 
- Easy deployment and scale-out in a Kubernetes Cluster
- Collect the baseline performance(Per Token Latancy) on SPR



<BR>


### GenAI Cloud Solution 
![Gen-AI-Soultion-4-240124](https://github.com/intel-sandbox/cloud.performance.workload.generative-ai.llm/assets/5109898/c9352033-5c78-4aac-87ec-93d01e56748b)








## 2. Deployment
### 2.1 Prerequisites
0. (optional) Setup Intel environment
1. Install Ubuntu 22.04 with containerd + cgroupv2 + RDT
2. Kubernetes v1.26 with One Node label with "llmdemo=true"
3. virtualenv,python3

### 2.2 Intel Harbor docker registry(OPT)
Be sure you can access the ccr-registry.caas.intel.com in k8s cluster.
Please refer to https://intel.sharepoint.com/sites/caascustomercommunity/sitepages/how-to-access.aspx?web=1


### 2.3 Init Envoirnment
Be sure to label one worker node of Kubernetes cluster with llmdemo=true

`kubectl labelnodes ${nodename} llmdemo=true`

Move the No-Schedule-Taint of master
`kubectl taint nodes {master-nodename}  node-role.kubernetes.io/control-plane:NoSchedule-
`

Be sure the virtualenv and python3 have been properly installed.

```
$ virtualenv -p python3 ./venv
$ . ./venv/bin/activate
$ pip install -rrequirements.txt
```
Be sure to install tools of the project
```
# need install ansible on master
# need init Resctrl on worker nodes
sudo mount -t resctrl resctrl /sys/fs/resctrl
sudo mkdir /sys/fs/resctrl/cri-resmgr.high

# need to install sysstat on worker nodes
sudo apt install sysstat
# need to install turbostat on worker nodes like this, please give the version of linux-tools
sudo install linux-intel-iotg-tools-common
sudo apt install linux-tools-5.15.0-79-generi
# need to install jq on node of load generator
sudo apt install jq
```

### 2.4 Init Model&Framework libs
We use slim image to increase the speed of downloading and deploying a llm pod.
You can use NFS service or not, here are two choices
If you choose use nfs, please do the section of "Setup NFS"
If not,ignore the following
#### Setup NFS(Optional)

Be Sure start public nfs service (nfs master node)
```
sudo apt update
sudo apt install nfs-kernel-server -y

sudo vim /etc/exports
----------------------------------------------------------
# add nfs config like this
/mnt 10.45.0.0/16(rw,no_root_squash,sync,no_subtree_check)
----------------------------------------------------------

systemctl restart nfs-kernel-server.service
# verify
systemctl status nfs-kernel-server.service
```

Be sure mount nfs (nfs slave node)
```
sudo apt update
sudo apt install nfs-kernel-server -y

sudo mount -t nfs 10.45.175.134:/mnt /mnt -o fsc

systemctl restart nfs-kernel-server.service
# verify
systemctl status nfs-kernel-server.service

```

#### 2.4.0 mount cifs
```
# 1.use command id to get current ${uid} and ${gid}
$ id
# 2. create folder of cifs_data  
$ mkdir -p ${LOCALPATH}/cifs_data
# 3. mount cifs
# before you mount , make sure you have copyright to access cifs
sudo mount -t cifs -o username=${user},uid=${uid},gid=${gid} "//shsfls0001.ccr.corp.intel.com/uServiceWL" ${LOCALPATH}/cifs_data
```
#### 2.4.1 Init Model
```
# make sure to download the model files to local path:/mnt/model/

$ cd ${LOCALPATH}/cifs_data/llm_service/models
$ sudo rsync -r . /mnt/model
```

### 2.4.2 Init Framework Libs
```
# make sure to download the framework library to local path:/mnt/miniconda3-docker
$ cd ${LOCALPATH}/cifs_data/llm_service/
$ sudo rsync -r libs /mnt/
$ tar -xvf libs.tar -C /mnt/miniconda3-docker
```



### 2.5 Single Deploy the LLM Workload & Check 
It's easy to deploy the llm workload. Say you want to deploy llama2-7B with openvion framework and bf16

0. Init intel’s helm chart harbor

     ```
     # please chose one of the methods
     # method 1
     helm repo add --ca-file <ca file> --cert-file <cert file> --key-file <key file>     --username <username> --password <password>  harbor_caas_intel  https://ccr-registry.caas.intel.com/chartrepo/cnbench
     
     # method 2
     helm repo add --username <username> --password <password>  harbor_caas_intel  https://ccr-registry.caas.intel.com/chartrepo/cnbench
     ```
1. Metric Collection&Dashboard(Optinal)

     ```
     helm pull harbor_caas_intel/kube-prometheus-stack
     helm install prometheus-stack kube-prometheus-stack-55.5.1.tgz
     ```
2. Ingress
     ```
     helm pull harbor_caas_intel/nginx-ingress
     helm install nginx-ingress nginx-ingress-0.18.0.tgz
     ```
     For Information, Please refer this doc of the Chart: Readme

3. LLM Deployment
     ```
     $ helm pull harbor_caas_intel/llm-deploy-chart
     $ tar -xvf llm-deploy-chart-0.1.0.tgz
     $ cd llm-deploy-chart
     $ cp values.yaml.llama2-7b-ov-bf16 values.yaml
     $ vim .helmignore
     # add '/venv' to ingnore the large file
     $ helm install llm-deploy-chart ./

     $ cd llm-deploy-chart
     $ ingressIP=`kubectl get svc|grep nginx-ingress-controller|awk '{print $3}'`
     $ ./replace_or_append_host.sh ${ingressIP} llm.intel.com
     ```
4. VERIFICATION

     ```
     curl -X POST "http://llm.intel.com/v2/completions" \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "What is AI?", "max_length":32, "history": []}'

     # Response will be like this:
     {"status":200,"prompt":"What is AI?","completion":"Artificial intelligence (AI) refers to the ability of a computer or machine to perform tasks that typically require human-like intelligence, such as understanding language, recognizing patterns","prompt_tokens":14,"completion_tokens":32,"total_dur_s":14.622767448425293,"total_token_latency_s":14.61293888092041,"first_token_latency_ms":3494.166612625122,"next_token_latency_ms":358.6700731708157,"avg_token_latency_ms":456.6543400287628}
     ```



### 3 benchmark by scenario file
We can easily get benchmark data for different combinations of models, frameworks, and precision by simply configuring scenario files.

Now we support the model matrix:
![Model Matrix-20240124](https://github.com/intel-sandbox/cloud.performance.workload.generative-ai.llm/assets/5109898/879ba649-362f-49b3-b3ed-68cb26598e38)



For more detail, please refer : https://github.com/intel-sandbox/cloud.performance.workload.generative-ai.llm/tree/main/llm-server


#### 3.0 config hosts
1. Please config the hosts using the real ip of your kubernetes:
     ```
     [job]
     172.16.28.130 # Master Node IP
     [emon]
     172.16.28.100 # Worker Node IP
     172.16.28.130 # Master Node IP
     [all:vars]
     ansible_ssh_common_args='-o StrictHostKeyChecking=no'
     ansible_ssh_private_key_file=/home/ansible/.ssh/id_rsa.team

     ```
2. Please make sure that current user can access the nodes by ssh and passwordless. We recommand the user name as "ansible".

#### 3.1 Usage of multi_deploy.py
```
     usage: multi_deploy.py [-h] [--log_file LOG_FILE] [--model_name MODEL_NAME] [--model_path MODEL_PATH] [--framework FRAMEWORK]
                         [--precision PRECISION] [--scale_type SCALE_TYPE] --max_instance MAX_INSTANCE --scenario_info SCENARIO_INFO
                         [--scenario_file SCENARIO_FILE] [--cpu_max CPU_MAX] [--cpu_step CPU_STEP] [--cpu_index CPU_INDEX]
                         [--cpu_reserved CPU_RESERVED] [--instance_cpu INSTANCE_CPU] [--iteration ITERATION] [--hyperthreading HYPERTHREADING]
                         --numa_order NUMA_ORDER [--benchmark_type BENCHMARK_TYPE] [--dry_run]

     options:
     -h, --help            show this help message and exit
     --log_file LOG_FILE, -l LOG_FILE
                         log file name
     --model_name MODEL_NAME, -n MODEL_NAME
                         model name: chatglm2-6b or llama2-7b
     --model_path MODEL_PATH, -P MODEL_PATH
                         model path
     --framework FRAMEWORK, -f FRAMEWORK
                         model framework: transformers|bigdl-llm-transformers|openvino
     --precision PRECISION, -p PRECISION
                         model data precision: fp16|int8|int4|bf16
     --scale_type SCALE_TYPE, -s SCALE_TYPE
                         scale type 0:scale by params 1:autoscale 2:deploy cpus
     --max_instance MAX_INSTANCE, -x MAX_INSTANCE
                         the scaled instance number should <= max_instance
     --scenario_info SCENARIO_INFO, -o SCENARIO_INFO
                         Briefly describe the test scenario. no more than 12 chars
     --scenario_file SCENARIO_FILE
                         read scenario setting from scenario_file, then benchmarking...
     --cpu_max CPU_MAX     cpu max number
     --cpu_step CPU_STEP   cpu value step
     --cpu_index CPU_INDEX
                         define cpu value
     --cpu_reserved CPU_RESERVED
                         reserved cpu not to be apply
     --instance_cpu INSTANCE_CPU, -c INSTANCE_CPU
                         cpus/threads each instance uses
     --iteration ITERATION, -i ITERATION
                         iteration count default:10
     --hyperthreading HYPERTHREADING, -y HYPERTHREADING
                         hyperthreading on/off 0:off 1:on default:0
     --numa_order NUMA_ORDER, -r NUMA_ORDER
                         numa order 0:numa0->numa1 1:numa0+numa1 default=0
     --benchmark_type BENCHMARK_TYPE, -t BENCHMARK_TYPE
                         0:only benchmark 1:deploy 2:deply+benchmark 3:only delete deploy
     --dry_run             Run the script in dry-run mode.

```



#### 3.2 Example: benchmark for single instance
there is already a example scenario file in the helmchart folder

0. the scenario file: scenarios-simple-check.json
     ```
     # after pull and extract the helmchart
     $ helm pull harbor_caas_intel/llm-deploy-chart
     $ tar -xvf llm-deploy-chart-0.1.0.tgz
     $ cd llm-deploy-chart/benchmark
     $ cat scenarios-simple-check.json
     
     "scenarios":
    [

        {
            "name" : "scenario1-testall-model-framework-precsion-prompts",
            "prefix" : "",
            "model_maps":
            [
            {
                "MODEL_NAME": "llama2-7b",
                "MODEL_PATH": "/models/Llama-2-7b-hf",
                "FRAMEWORK": "transformers",
                "MODEL_DTYPE": "fp16"
            },
            {
                "MODEL_NAME": "llama2-7b",
                "MODEL_PATH": "/models/Llama-2-7b-hf",
                "FRAMEWORK": "transformers",
                "MODEL_DTYPE": "bf16"
            },
            ...

            ],
            "iteration" : 1,
            "numa_order" : 0,
            "hyperthreading" : 0,
            "benchmark_type" : 0,
            "scale_type" : 2,
            "cpu_max": 224,
            "cpu_step": 8,
            "cpu_index" :56,
            "prompt_keys": ["30:2"]
        }
    ]

     ```
     In this scenario config file, you could set all the model combinations.
     the other important parameters are:
     - iteration - test times of each model map
     - numa_order - means to use the cpus in same numa or distribute to 2 numas (please leave it to 0)
     - hyperthreading - means to use hypertheading or not. the value 0 means it only use each core's one vcpu.(Unless you know what you are doing, please leave this parameter to 0.)
     - scale_type - 2: To scale single instance set cpu from cpu_step to cpu_max, the default cpu_step is 8 (8,16,24....)
		if the cpu_index is set and in one of those cpu numbers. the script will only use this config to do benchmark.   0: To Scale multi instance. 
     - cpu_max: - tell the script how many vcpus the server has.(224 for SPR)
     - cpu_step: - cpu step value when the pod will use for each benchmark(e.q. 8,16,24 ...)
     - cpu_index - set cpu_index if you just want to test pod for specific cpu num
     - prompt_keys - the index of pre defined prompts map

1. how to benchmark?
     ```
     $ cd llm-deploy-chart/benchmark
     $ python multi_deploy.py --scenario_file="./scenarios-simple-single-run.json" -x 224 -o "scenarios-simple-single-run" -r 0 -s 2
     ```

2. how to collect metrics from logfile?
     ```
     # let's say the logfile is multi_deploy.log.20240116154539_m2v7
     $ LOGFILE=multi_deploy.log.20240116154539_m2v7
     $ grep "response_data=" $LOGFILE|grep -oP "{.*}"|sed "s/'/\"/g" | jq -r '"\(.prompt_tokens) \(.completion_tokens) \(.total_dur_s) \(.total_token_latency_s) \(.first_token_latency_ms) \(.next_token_latency_ms) \(.avg_token_latency_ms)"'

     # the metrics result of each scenario will be like this:
     22 32 4.978836606256664 4.97351757157594 290.8925348892808 151.0524205382793 155.42242411174811
     22 32 4.095557054504752 4.0933232847601175 193.0547021329403 125.81511556861862 127.91635264875367
     22 32 2.1805072212591767 2.177922686561942 227.53984481096268 62.915575540354176 68.06008395506069
     22 32 1.550695851445198 1.5481982920318842 218.5098547488451 42.893175396227065 48.38119662599638
     ...
     ```
3. How to collect CPU,Memory Bandwidth usage info?
     ```
     # The CPU,Mem BW usage info will be logged into ~/llm_metrics, the folder name will have the same Timestamp and four chars token:m2vp,like this: mtr_20240116154539_m2v7_scenario012/

     # 1. sync the logs from worker to localpath in master node
     rsync -r 172.16.28.130:~/llm_metrics {localpath}/ -P

     # 2. get Memeory Bandwidth Usage
     $ FOLDER=${localpath/mtr_20240116154539_m2v7_scenario012/}


     $ find $FOLDER -name "memrdt.log"|sort|xargs -I {} python3 process_metrics.py -t MEMBW  -m {} 2>&1 |grep -E "Total Maximum mem_bw_total"|awk -F'[[:space:]]+' '{print $4}'

     the result of Memory Bandwidth usage would be like this:
     Total Maximum mem_bw_total: 173070.00 MB
     Total Maximum mem_bw_total: 120266.00 MB
     Total Maximum mem_bw_total: 110367.00 MB
     Total Maximum mem_bw_total: 66591.00 MB
     Total Maximum mem_bw_total: 120049.00 MB
     Total Maximum mem_bw_total: 73736.00 MB
     Total Maximum mem_bw_total: 177254.00 MB
     Total Maximum mem_bw_total: 135715.00 MB
     Total Maximum mem_bw_total: 104792.00 MB
     Total Maximum mem_bw_total: 80645.00 MB
     Total Maximum mem_bw_total: 121340.00 MB
     Total Maximum mem_bw_total: 76478.00 MB   
     ...

     # 3. get CPU Utilization Usage 
     find $FOLDER -name "cpu_freq.log"|sort|xargs -I {} python process_metrics.py -f {} -t CPUUTIL  2>&1 |grep "max_cpu"|awk -F'[:,]' '/avg_cpu/ {print $4}'


     ```




     
#### 3.3 Example: benchmark for multi instance

0. the scenario file: scenarios-multi-instance.json
     ```
     # after pull and extract the helmchart
     $ helm pull harbor_caas_intel/llm-deploy-chart
     $ tar -xvf llm-deploy-chart-0.1.0.tgz
     $ cd llm-deploy-chart/benchmark
     $ cat scenarios-multi-instance.json
     

     "scenarios":
    [

        {
            "name" : "llama2-7b fp32 instances2",
            "prefix" : "",
            "model_maps":
            [
                {
                    "MODEL_NAME": "llama2-7b",
                    "MODEL_PATH": "/models/Llama-2-7b-hf",
                    "FRAMEWORK": "transformers",
                    "MODEL_DTYPE": "fp32"
                }
            ],
            "iteration" : 3,
            "numa_order" : 0,
            "hyperthreading" : 0,
            "benchmark_type" : 2,
            "instance_cpu" : 56,
            "max_instance" : 4,
            "scale_type" : 0,
            "cpu_max": 224,
            "prompt_keys": ["30:2"]
        },
        {
            "name" : "llama2-7b int4 instances10",
            "prefix" : "",
            "model_maps":
            [
                {
                    "MODEL_NAME": "llama2-7b",
                    "MODEL_PATH": "/models/Llama-2-7b-hf",
                    "FRAMEWORK": "bigdl-llm-transformers",
                    "MODEL_DTYPE": "int4"
                }
            ],
            "iteration" : 3,
            "numa_order" : 0,
            "hyperthreading" : 0,
            "benchmark_type" : 2,
            "instance_cpu" : 10,
            "max_instance" : 10,
            "scale_type" : 0,
            "cpu_max": 224,
            "prompt_keys": ["30:2"]
        }

     ```
     In this multi-instance scenario config file, you could find that is is different from the single instance scenairo configfile. The reason is that for deploy multi instance of each scenario, the instance number,cpu num will be different.  
     the  important parameters are:
     - iteration - test times of each model map
     - numa_order - means to use the cpus in same numa or distribute to 2 numas (please leave it to 0)
     - hyperthreading - means to use hypertheading or not. the value 0 means it only use each core's one vcpu.(Unless you know what you are doing, please leave this parameter to 0.)
     - benchmark_type - 0:only benchmark 1:deploy 2:deply+benchmark 3:only delete deploy 
     - scale_type - 2: To scale single instance set cpu from cpu_step to cpu_max, the default cpu_step is 8 (8,16,24....)
		if the cpu_index is set and in one of those cpu numbers. the script will only use this config to do benchmark.   0: To Scale multi instance. 
     - cpu_max: - tell the script how many vcpus the server has.(224 for SPR)
     - prompt_keys - the index of pre defined prompts map

1. how to benchmark?
     ```
     $ cd llm-deploy-chart/benchmark
     $ python multi_deploy.py --scenario_file="./scenarios-multi-instance.json"  -o "scenarios-multi-instance-matrix12" -x 224 -r 0
     ```

2. how to collect metrics from logfile?

     Because in each sceanario,there are many instances will be running. So the latency metrics will be the average value.

     ```
     # let's say the logfile is multi_deploy.log.20240115182049_t0vq
     $ LOGFILE=multi_deploy.log.20240115182049_t0vq
     $ grep "The Average Metric" multi_deploy.log.20240115182049_t0vq|awk -F':' '{print $NF}'

     # the metrics result of each scenario will be like this:
     22.00,32.00,5.15,5.15,294.98,156.55,160.88 
     22.00,32.00,3.80,3.79,157.24,117.30,118.55 
     22.00,32.00,2.70,2.70,283.52,77.82,84.25 
     22.00,32.00,3.45,3.45,570.29,92.79,107.72 
     22.00,32.00,3.76,3.76,143.34,112.89,113.82 
     22.00,32.00,3.84,3.84,149.85,115.40,116.44 
     22.00,32.00,4.49,4.49,223.95,137.49,140.19 
     22.00,32.00,3.18,3.18,229.48,95.22,99.41 
     22.00,32.00,2.44,2.44,234.42,71.01,76.12 
     22.00,32.00,3.15,3.14,493.29,85.53,98.27 
     36.00,33.00,3.45,3.44,196.90,101.50,104.39 
     36.00,28.00,2.93,2.93,177.37,102.05,104.74
     ...
     ```
     
3. How to collect CPU,Memory Bandwidth usage info?
     ```
     # The CPU,Mem BW usage info will be logged into ~/llm_metrics, the folder name will have the same Timestamp and four chars token:m2vp,like this: mtr_20240115182049_t0vq_scenario012/

     # 1. sync the logs from worker to localpath in master node
     rsync -r 172.16.28.130:~/llm_metrics {localpath}/ -P

     # 2. get Memeory Bandwidth Usage
     $ FOLDER=${localpath/mtr_20240115182049_t0vq_scenario012/}


     $ find $FOLDER -name "memrdt.log"|sort|xargs -I {} python3 process_metrics.py -t MEMBW -m {} 2>&1 \
     |grep -E "Total Maximum mem_bw_total"

     the result of Memory Bandwidth usage would be like this:
     Total Maximum mem_bw_total: 346038.00 MB
     Total Maximum mem_bw_total: 235690.00 MB
     Total Maximum mem_bw_total: 359217.00 MB
     Total Maximum mem_bw_total: 378826.00 MB
     Total Maximum mem_bw_total: 237317.00 MB
     Total Maximum mem_bw_total: 237237.00 MB   
     ...

     # 3. get CPU Utilization Usage 
     find $FOLDER -name "cpu_freq.log"|sort|xargs -I {} python process_metrics.py -f {} -t CPUUTIL  2>&1 |grep "max_cpu"|awk -F'[:,]' '/avg_cpu/ {print $4}'
     ```








