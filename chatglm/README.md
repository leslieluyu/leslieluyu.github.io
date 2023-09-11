# Deployment Guide 
## 1. Overview

Target:
- A containerized Cloud native generative AI large language models(LLM) workload 
- Easy deployment and scale-out in a Kubernetes Cluster
- Collect the baseline performance(Per Token Latancy) on SPR



## 2. Deployment
### 2.1 Prerequisites
0. (optional) Setup Intel environment
1. Install Ubuntu 22.04 with containerd + cgroupv2
2. Kubernetes v1.26

### 2.2 Intel Harbor docker registry
Please refer to https://intel.sharepoint.com/sites/caascustomercommunity/sitepages/how-to-access.aspx?web=1

### 2.3 K8s-dashboard
```
$ cd k8s-dashboard
$ kubectl apply -f dashboard-deploy.yaml
$ kubectl apply -f dashboard-adminuser.yaml
$ kubectl apply -f dashboard-rbac.yaml
```

### 2.4 Prometheus&Grafana
```
$ cd kube-prometheus
$ kubectl apply --server-side -f manifests/setup/
$ kubectl apply -f manifests/
```

### 2.5 Kubernetes-ingress
please refer this guide https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-manifests/

### 2.6 Setup the CPU-Manager
```
$ cd cpu-manager
$ ./enablecpumgr.sh
```

### 2.7 Deploy the LLM workload
```
$ cd llm_deploy
$ kubectl apply -f llm_deploy_metrics.yaml
# setup monitor
$ kubectl apply -f monitor.yaml
```
How to Verify the workload
```
$ curl -X POST "http://llm.intel.com/v1/completions" \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "What is AI?", "history": []}'
```

### 2.8 Benchmark (TODO)


## 3. Architecture
