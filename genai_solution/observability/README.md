
# How-To Setup Observability for OPEA Workload in Kubernetes
This guide provides a step-by-step approach to setting up observability for the OPEA workload in a Kubernetes environment. We will cover the setup of Prometheus and Grafana, as well as the collection of metrics for Gaudi hardware, OPEA/chatqna including TGI,TEI-Embedding,TEI-Reranking and other microservies, and PCM.

## 1. Setup Prometheus & Grafana
Setting up Prometheus and Grafana is essential for monitoring and visualizing your workloads. Follow these steps to get started:

Step 1: Install Prometheus&Grafana
```
cd prometheus_grafana
kubectl create ns monitoring
helm install prometheus-stack kube-prometheus-stack-55.5.1.tgz -n monitoring
```

Step 2: Verify the installation:
```bash
kubectl get pods -n monitoring 
```

Step 3: Port-forward to access Grafana:
```
bash
kubectl port-forward service/grafana 3000:80
```


Step 4: Access Grafana:
Open your browser and navigate to http://localhost:3000. Use "admin/prom-operator" as the username and the password to login.

## 2. Metric for Gaudi Hardware(v1.16.2)
To monitor Gaudi hardware metrics, you can use the following steps:

Step 1: Install daemonset
``` 
kubectl create -f https://vault.habana.ai/artifactory/gaudi-metric-exporter/yaml/1.16.2/metric-exporter-daemonset.yaml
```


Step 2: Install metric-exporter
```
kubectl create -f https://vault.habana.ai/artifactory/gaudi-metric-exporter/yaml/1.16.2/metric-exporter-service.yaml
```

Step 3: Install service-monitor
```
kubectl apply -f ./habana/metric-exporter-serviceMonitor.yaml
```
Step 4: Verify the metrics
```
# To get the metric endpoints
kubectl get ep -n monitoring |grep metric-exporter
# Fetch the metrics
curl ${metric_exporter_ip}:41611/metrics 

# you will see the habana metric data  like this:
process_resident_memory_bytes 2.9216768e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.71394960963e+09
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.862641152e+09
# HELP process_virtual_memory_max_bytes Maximum amount of virtual memory available in bytes.
# TYPE process_virtual_memory_max_bytes gauge
process_virtual_memory_max_bytes 1.8446744073709552e+19
# HELP promhttp_metric_handler_requests_in_flight Current number of scrapes being served.
# TYPE promhttp_metric_handler_requests_in_flight gauge
promhttp_metric_handler_requests_in_flight 1
# HELP promhttp_metric_handler_requests_total Total number of scrapes by HTTP status code.
# TYPE promhttp_metric_handler_requests_total counter
promhttp_metric_handler_requests_total{code="200"} 125
promhttp_metric_handler_requests_total{code="500"} 0
promhttp_metric_handler_requests_total{code="503"} 0
```

Step 5: Import the dashboard into Grafana 
Manually import ./habana/Dashboard-Gaudi-HW.json into Grafana

## 3. Metric for OPEA/chatqna

## 4. Metric for PCM
