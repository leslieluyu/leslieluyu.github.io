import requests

namespace = "default"
prometheus_url = "http://10.45.247.81:31090"

query = 'avg_over_time(rate(container_cpu_usage_seconds_total{namespace="default", container!="POD"}[1m])[2m:]) by (pod)'
url = prometheus_url + "/api/v1/query?query=" + query

response = requests.get(url).json()
if response["status"] != "success":
    print("Error: failed to fetch data from Prometheus API")
    exit(1)

results = response["data"]["result"]
for result in results:
    pod_name = result["metric"]["pod"]
    cpu_usage = result["value"][1]
    print("Pod %s CPU utilization: %s" % (pod_name, cpu_usage))