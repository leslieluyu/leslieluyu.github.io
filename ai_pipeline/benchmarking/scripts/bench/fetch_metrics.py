import requests
import argparse
import time
import psutil

# Define command line arguments
parser = argparse.ArgumentParser(description='Fetch pod metrics from Prometheus API')
parser.add_argument('-P', '--Path',default='metrics', required=True, help='metrics path')
parser.add_argument('-s', '--scenario',default='default', required=True, help='Scenario AMX_BF16,NON,VNNI_INT8')
parser.add_argument('-n', '--namespace',default='default', required=False, help='Kubernetes namespace')
parser.add_argument('-u', '--url', default='10.45.247.81', required=False, help='Prometheus API URL')
parser.add_argument('-p', '--port', default='31090', required=False, help='Prometheus API port')
parser.add_argument('-t', '--time', default='2m', required=False, help='Time range till now, for example:60s or 2m ')
args = parser.parse_args()


# Set values from arguments provided
path = args.Path
scenario = args.scenario
namespace = args.namespace
prometheus_url = f'http://{args.url}:{args.port}'
port = args.port
time_range = args.time

# Define metrics to fetch
metrics = ['cpu_usage', 'memory_usage','ei_infer_fps', 'ei_drop_fps', 'ei_scale_ratio' ]

# Define query for CPU usage

#cpu_query = f'sum(rate(container_cpu_usage_seconds_total{{namespace="{args.namespace}"}}[{args.time}])) by (pod)'
cpu_query = f'avg_over_time(rate(container_cpu_usage_seconds_total{{namespace="{args.namespace}", container!=""}}[{args.time}])[{args.time}:])'

# Define query for memory usage
mem_query = f'sum(container_memory_working_set_bytes{{namespace="{args.namespace}",container!="", image!=""}}) by (pod) '

# Define query for other metrics
#                 f'sum(ei_drop_fps{{namespace="{args.namespace}"}}[{args.time}]) by (pod)',
other_queries = [f'avg_over_time(ei_infer_fps{{namespace="{args.namespace}"}}[{args.time}])',
                 f'avg_over_time(ei_drop_fps{{namespace="{args.namespace}"}}[{args.time}])',
                 f'avg_over_time(ei_scale_ratio{{namespace="{args.namespace}"}}[{args.time}])']
# avg_over_time(ei_drop_fps{namespace="default"}[2m])
# Fetch metrics from Prometheus API
results = {}




for metric,query in zip(metrics, [cpu_query, mem_query] + other_queries):
    url = f'{prometheus_url}/api/v1/query?query={query}'
    print(f"The query to fetch metrics from prometheus is: {url}")
    try:    
        response = requests.get(url).json()
        if response['status'] != 'success':
            print(f'Error: failed to fetch data from Prometheus API for query {query}')
            continue
        #metric_name = query.split('{')[0].split('(')[-1]
        metric_name = metric
        results[metric_name] = response['data']['result']
        print(f"metric_name is: {metric_name}")
        print(f"result is: {results[metric_name]}")
    except json.JSONDecodeError as e:
        print(f"Error: failed to parse JSON response from Prometheus API: {e}")
        exit(1)
    except Exception as e:
        print(f"Error: failed to fetch data from Prometheus API: {e}")
        exit(1)


# Write metrics to output file
output_filename = f"{path}/{scenario}_metrics_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_filename, "w") as f:
    f.write("# Metrics for Kubernetes namespace %s\n" % namespace)
    f.write("# Timestamp: %s\n" % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write("# Prometheus URL: %s\n" % prometheus_url)
    f.write("# Prometheus port: %s\n" % port)
    f.write("# Time range: %s \n" % time_range)
    f.write("#\n")
    
    for result, metric in zip(results, metrics):
        f.write(f"# {metric}\n")
        for pod_result in results[result]:
            pod_name = pod_result['metric']['pod']
            value = pod_result['value'][1]
            f.write(f"{pod_name} {metric} {value}\n")

print(f'Results written to {output_filename}')

'''
    for pod_result in results['container_cpu_usage_seconds_total']:
        pod_name = pod_result['metric']['pod']
        cpu_usage = pod_result['value'][1]
        mem_result = [r for r in results['container_memory_working_set_bytes'] if r['metric']['pod'] == pod_name]
        if mem_result:
            memory_usage = mem_result[0]['value'][1]
        else:
            memory_usage = 'N/A'
        other_results = [r for metric_name in metrics if metric_name not in ['cpu_usage', 'memory_usage']
                         for r in results[metric_name] if r['metric']['pod'] == pod_name]
        if not all(other_results):
            continue
        
        ei_infer_fps, ei_drop_fps, ei_scale_ratio = other_results[0]['value'][1]
        ei_drop_fps = other_results[1]['value'][1]
        ei_infer_fps = other_results[2]['value'][1]
        f.write(f'{pod_name}\t{ei_infer_fps}\t{ei_drop_fps}\t{ei_scale_ratio}\t{cpu_usage}\t{memory_usage}\n')

'''