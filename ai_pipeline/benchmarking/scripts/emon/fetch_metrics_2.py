import requests
import argparse
import time

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--namespace", help="Kubernetes namespace to query")
parser.add_argument("--prometheus_url", help="Prometheus server URL")
parser.add_argument("--port", help="Prometheus server port")
parser.add_argument("--time", type=str, default="2m", help="Time range to query (in seconds)")
args = parser.parse_args()

# Set default values if no arguments provided
namespace = args.namespace or "default"
prometheus_url = args.prometheus_url or "http://10.45.247.81"
port = args.port or 31090
time_range = args.time or "2m"



metrics = ['cpu_usage', 'memory_usage','ei_infer_fps', 'ei_drop_fps', 'ei_scale_ratio', ]

# Build Prometheus query
# avg_over_time(rate(container_cpu_usage_seconds_total{namespace="default", container!="POD"}[2m])[2m:]) 
query = 'avg_over_time(rate(container_cpu_usage_seconds_total{namespace="%s", container!=""}[%s])[%s:])' % (namespace, time_range, time_range)


#query = 'sum(rate(container_cpu_usage_seconds_total{namespace="%s"}[%ds])) by (pod)' % (namespace, time_range)
#query += '\nsum(container_memory_working_set_bytes{namespace="%s"}) by (pod)' % namespace
#query += '\nei_infer_fps{namespace="%s"}' % namespace
#query += '\nei_drop_fps{namespace="%s"}' % namespace
#query += '\nei_scale_ratio{namespace="%s"}' % namespace
#query += '\nsum(rate(container_cpu_usage_seconds_total{namespace="%s"}[%ds])) by (pod, container)' % (namespace, time_range)
#query += '\nsum(container_memory_working_set_bytes{namespace="%s"}) by (pod, container)' % namespace

# Make API call to Prometheus server
url = f"{prometheus_url}:{port}/api/v1/query?query={query}"
response = requests.get(url).json()

# Check if response is successful
if response["status"] != "success":
    print("Error: failed to fetch data from Prometheus API")
    exit(1)

# Write metrics to output file
output_filename = f"{namespace}_metrics_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_filename, "w") as f:
    f.write("# Metrics for Kubernetes namespace %s\n" % namespace)
    f.write("# Timestamp: %s\n" % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write("# Prometheus URL: %s\n" % prometheus_url)
    f.write("# Prometheus port: %s\n" % port)
    f.write("# Time range: %s \n" % time_range)
    f.write("#\n")
    results = response["data"]["result"]
    #print(f"result is : %s\n" % (results))
    for result, metric in zip(results,metrics):
        metric_name = metric #result["metric"].get("__name__", "")
        pod_name = result["metric"].get("pod", "")
        container_name = result["metric"].get("container", "")
        metric_value = result["value"][1]
        print(f"%s,%s,%s,%s\n" % (metric_name, pod_name, container_name, metric_value))
        f.write("%s,%s,%s,%s\n" % (metric_name, pod_name, container_name, metric_value))
