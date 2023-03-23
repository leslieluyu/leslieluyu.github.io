import argparse
import subprocess
import time
from kubernetes import client, config


def set_deployment_env(namespace, deploy_name, scenario):


    # Load the Kubernetes configuration and create the API client
    config.load_kube_config()
    api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    

    # Get the deployment object
    deployment = api.read_namespaced_deployment(name=deploy_name, namespace=namespace)
    # Get the deployment object
    # deployment = client.AppsV1Api().read_namespaced_deployment(name=deploy_name, namespace=namespace)


    # set the environment variables for each scenario
    print(f"Setting environment variables for scenario {scenario['scenario_name']}...")
    patch_body = [{"op": "add", "path": "/spec/template/spec/containers/0/env", "value": scenario["envs"]}]
    api.patch_namespaced_deployment(name=deploy_name, namespace=namespace, body=patch_body)

    # Wait for the pods to be ready
    pods_ready = False
    while not pods_ready:
        pods = core_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={deploy_name}")
        ready_pods = [pod for pod in pods.items if pod.status.phase == "Running" and pod.status.conditions[-1].status == "True"]
        if len(ready_pods) == deployment.spec.replicas:
            print(f"All {deployment.spec.replicas} pods are ready for scenario {scenario['scenario_name']}")
            pods_ready = True
        else:
            print(f"Waiting for {deployment.spec.replicas - len(ready_pods)} more pods to be ready for scenario {scenario['scenario_name']}...")
            time.sleep(10)





if __name__ == "__main__":
    print(f'the arguments: ')

    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="default", help="the namespace of the deployment")
    parser.add_argument("--deploy_name", default="ei-infer-deployment-pose-bf16-amx-01", help="the name of the deployment")
    args = parser.parse_args()

    print(f'the arguments: {args}')
    # Define the scenarios and their environment variables
    scenarios = [
        {
            "scenario_name": "AMX_BF16",
            "envs": [
                {"name": "ONEDNN_MAX_CPU_ISA", "value": "AVX512_CORE_AMX"},
                {"name": "INFER_MODEL_NAME", "value": "ssd_mobilenet_bf16"},
            ],
        }

    ]

    # Iterate over the scenarios and set the deployment env
    for scenario in scenarios:
        print(f"Begin set_deployment_env of scenario: {scenario['scenario_name']} ...")
        set_deployment_env(args.namespace, args.deploy_name, scenario)
        print(f"Finished scenario {scenario['scenario_name']}")
        
        # Call the benchmarking script
        print(f"Running benchmarking script for scenario {scenario['scenario_name']}...")
        subprocess.run(["./loop_benchmarking.sh"])

    print("Finished running all scenarios!")
    