# stresscli/load_test.py

import os
import subprocess
import click
import yaml
from datetime import datetime
from .report import export_testdata, folder_report
from .utils import dump_k8s_config, generate_random_suffix, generate_lua_script
from .metrics import MetricsCollector
from .metrics_util import export_metric
from .pcm_util import start_pcm, finish_pcm
from .utilization import  MetricFetcher


# Define default values
locust_defaults = {
    'locustfile': 'locustfile.py',
    'host': 'http://127.0.0.1:8888',
    'stop-timeout': 120,
    'run-time': '48h',
    'processes': 2 ,
    'bench-target': 'mega_chatqna_fixed',
    'users': 10,
    'max-request': 100,
    'namespace': 'default',
}
    

@click.command()
#@click.option('--dataset', type=click.Path(), help='Dataset path')
#@click.option('--endpoint', type=click.Path(), help='Endpoint of the test target service, like "http://192.168.0.12:8888/chatqna"')
@click.option('--profile', type=click.Path(), help='Path to profile YAML file')
@click.pass_context
#@click.option('--kubeconfig', type=click.Path(), help='Configuration file to Kubernetes')
def load_test(ctx, profile):
    """Do load test"""
    kubeconfig = ctx.parent.params['kubeconfig']
    locust_runtests(kubeconfig, profile)


def locust_runtests(kubeconfig, profile):
    if profile:
        with open(profile, 'r') as file:
            profile_data = yaml.safe_load(file)

        # create test log folder
        hostpath = profile_data['profile']['storage']['hostpath']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_folder = os.path.join(hostpath, f"{timestamp}")
        os.makedirs(base_folder, exist_ok=True)
        profile_dump = os.path.join(base_folder, "0_profile.yml")

        with open(profile_dump, 'w') as dump_yaml:
            yaml.dump(profile_data, dump_yaml)

        # Extract storage path and run details from profile
        global_settings = profile_data['profile']['global-settings']
        runs = profile_data['profile']['runs']
        
        index = 1
        for run in runs:
            print(f"===Starting test: {run['name']}")
            run_locust_test(kubeconfig, global_settings, run, base_folder, index)
            print(f"===Completed test: {run['name']}")
            index = index + 1

        # folder_report(base_folder, 'html', f"{base_folder}/0_benchmark_report.html", profile_dump)
        # folder_report(base_folder, 'csv', f"{base_folder}/0_benchmark_result.csv")
        click.echo(f'Load test results saved to {base_folder}')

def collect_metrics(collector, namespace, services, output_dir):
    collector.start_collecting_data(
        namespace=namespace,
        services=services,
        output_dir=output_dir,
        restart_pods_flag=False,
    )

def run_locust_test(kubeconfig, global_settings, run_settings, output_folder, index):
    # Merge settings with priority: run_settings > global_settings > defaults
    runspec={}
    runspec['tool'] = 'locust'
    runspec['locustfile'] = run_settings.get('locustfile', global_settings.get('locustfile', locust_defaults['locustfile']))
    runspec['host'] = run_settings.get('host', global_settings.get('host', locust_defaults['host']))
    runspec['runtime'] = run_settings.get('run-time', global_settings.get('run-time', locust_defaults['run-time']))
    runspec['users'] = run_settings.get('users', global_settings.get('users', locust_defaults['users']))
    runspec['max_requests'] = run_settings.get('max-request', global_settings.get('max-request', locust_defaults['max-request']))
    runspec['stop_timeout'] = run_settings.get('stop-timeout', global_settings.get('stop-timeout', locust_defaults['stop-timeout']))
    runspec['processes'] = run_settings.get('processes', global_settings.get('processes', locust_defaults['processes']))
    runspec['bench-target'] = run_settings.get('bench-target', global_settings.get('bench-target', locust_defaults['bench-target']))
    runspec['namespace'] = run_settings.get('namespace', global_settings.get('namespace', locust_defaults['namespace']))

    runspec['run_name'] = run_settings['name']
    #csv_output = os.path.join(output_folder, runspec['run_name'])
    #json_output = os.path.join(output_folder, f"{runspec['run_name']}_output.log")
    csv_output = os.path.join(output_folder, f'{index}')
    json_output = os.path.join(output_folder, f"{index}_output.log")
    util_output = os.path.join(output_folder, f"{index}_utilization.log")

    service_metric = global_settings.get('service-metric-collect', False)
    if service_metric:
        metrics_output_folder = os.path.join(output_folder, f"{index}_metrics")
        os.makedirs(metrics_output_folder, exist_ok=True)
        start_output_folder = os.path.join(metrics_output_folder, "start")
        os.makedirs(start_output_folder, exist_ok=True)
        end_output_folder = os.path.join(metrics_output_folder, "end")
        os.makedirs(end_output_folder, exist_ok=True)
        metrics_output = os.path.join(output_folder, f"{index}_metrics.json")

    pcm_metric = global_settings.get('pcm-metric-collect', False)
    if pcm_metric:
        pcm_metrics_folder = os.path.join(output_folder, f"{index}_pcm_metrics")
        os.makedirs(pcm_metrics_folder, exist_ok=True)
        pcm_ns = global_settings.get('pcm-namespace', 'pcm')
    cmd = [
        'locust',
        '--locustfile', runspec['locustfile'],
        '--host', runspec['host'],
        '--run-time', runspec['runtime'],
        '--users', str(runspec['users']),
        '--spawn-rate', str(runspec['users']),
        '--max-request', str(runspec['max_requests']),
        '--processes', str(runspec['processes']),
        '--bench-target', str(runspec['bench-target']),
        '--stop-timeout', str(runspec['stop_timeout']),
        '--csv', csv_output,
        '--headless',
        '--only-summary',
        '--loglevel', 'WARNING',
        '--json'
    ]

    print(f"Running test: {' '.join(cmd)}")
    namespace = runspec['namespace']

    if service_metric:
        collector = MetricsCollector()
        services = global_settings.get('service-list') or []
        service_list = []
        if isinstance(services, dict):
            for key, value in services.items():
                # Add the key to the list
                service_list.append(key)
                if isinstance(value, list):
                    for it in value:
                        service_list.append(it)
            services = list(set(service_list))

        collect_metrics(collector, namespace, services, start_output_folder)

    if pcm_metric:
        start_pcm(pcm_metrics_folder, pcm_ns)

    metrics_endpoint = "http://192.168.180.115:9100/metrics"  # Replace with your endpoint
    
    fetcher = MetricFetcher(metrics_endpoint)
    print(f"before start_collect_utilization:")
    start_collect_utilization(fetcher)


    runspec['starttest_time'] = datetime.now().isoformat()
    result = subprocess.run(cmd, capture_output=True, text=True)
    runspec['endtest_time'] = datetime.now().isoformat()

    print(f"before stop_collect_utilization: {util_output}")
    stop_collect_utilization(fetcher,util_output)

    if pcm_metric:
        finish_pcm()

    if service_metric:
        collect_metrics(collector, namespace, services, end_output_folder)
        export_metric(start_output_folder, end_output_folder, metrics_output_folder, metrics_output, services)

    with open(json_output, 'w') as json_file:
        json_file.write(result.stderr)
        json_file.write(result.stdout)
    print(result.stderr)
    print(result.stdout)
    dump_test_spec(kubeconfig,runspec,runspec['namespace'],output_folder,index)



def start_collect_utilization(fetcher):
    # Start the MetricFetcher
    fetcher.start(
        metric_names=["rdt_container_cpu_utilization", "rdt_container_local_memory_bandwidth"],
        namespace="benchmarking"
    )
def stop_collect_utilization(fetcher,result_file_path):
    # Stop the MetricFetcher
    fetcher.stop()

    # Calculate and print average and max per container
    stats = fetcher.calculate_average_and_max_per_container()

    # Save results to a file
    print(f"Calculated Average and Max per Container:")
    fetcher.save_results_to_file(stats, result_file_path)
    print(f"after save_results_to_file {result_file_path}")

def dump_test_spec(kubeconfig, run, namespace, output_folder,index):
    # Dump the k8s spec
    k8s_spec = dump_k8s_config(kubeconfig, return_as_dict=True, namespace=namespace)
    # Check if k8s_spec contains the expected keys
    hardware_spec = k8s_spec.get('hardwarespec', {})
    workload_spec = k8s_spec.get('workloadspec', {})

    data_output=export_testdata(f'{index}', output_folder, 'output.log|stats.csv')
    # Combine both specs into a single YAML file
    combined_spec = {
        'benchmarkspec': run,
        'benchmarkresult': data_output,
        'hardwarespec': hardware_spec,
        'workloadspec': workload_spec
    }
    combined_spec_path = os.path.join(output_folder, f'{index}_testspec.yaml')
    with open(combined_spec_path, 'w') as combined_file:
        yaml.dump(combined_spec, combined_file)

    
def wrk_runtests(kubeconfig,dataset, endpoint, profile):
    if dataset:
        click.echo(f'Using dataset: {dataset}')

    # Here you would add the logic to perform the load test
    if profile:
        with open(profile, 'r') as file:
            profile_data = yaml.safe_load(file)

        # create test log folder
        hostpath = profile_data['profile']['storage']['hostpath']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_folder = os.path.join(hostpath, f"{timestamp}")
        os.makedirs(base_folder, exist_ok=True)
        
        # Extract storage path and run details from profile
        runs = profile_data['profile']['runs']
        
        for run in runs:
            run_name = run['name']
            namespace = run.get('namespace','default')
            loop = run.get('loop', 1)
            tool = run.get('tool', 'wrk')
            options = run['options']
            endpoint = run['endpoint']
            dataset = run.get('dataset', dataset)
            lua_template_path = run.get('luatemplate', '/home/sdp/workspace/OPEAStress/stresscli/lua_template/chatqna.template')
            
            # Create the folder for the run
            run_folder = os.path.join(base_folder, f"{run_name}")
            os.makedirs(run_folder, exist_ok=True)

            # Generate Lua script
            lua_script_path = os.path.join(run_folder, "wrk_script.lua")
            generate_lua_script(lua_template_path, lua_script_path, dataset)   

            for i in range(loop):
                # Generate wrk command and execute it
                wrk_command = f'{tool} {options} --script {lua_script_path} {endpoint}'
                print(wrk_command)
                wrk_log_path = os.path.join(run_folder, f'wrk_{i + 1}.log')
                with open(wrk_log_path, 'w') as wrk_log:
                    subprocess.run(wrk_command.split(), stdout=wrk_log, stderr=subprocess.STDOUT)

            dump_test_spec(kubeconfig,run,namespace,run_folder)   
        click.echo(f'Load test results saved to {base_folder}')
    else:
        click.echo('Profile is required to run the test.')
