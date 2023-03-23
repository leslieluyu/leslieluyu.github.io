import argparse
import subprocess
import time
import json
import logging
from datetime import datetime
from kubernetes import client, config
from pprint import pprint
import random



def set_deployment_env(namespace, deploy_name, app_name, scenario):
    # Load the Kubernetes configuration and create the API client
    config.load_kube_config()
    api = client.AppsV1Api()
    core_api = client.CoreV1Api()

    # Get the deployment object
    deployment = api.read_namespaced_deployment(name=deploy_name, namespace=namespace)

    # Set the environment variables for the scenario
    logger.info(f"Setting environment variables for scenario {scenario['scenario_name']}...")
    # Set the environment variables
    # containers = deployment.spec.template.spec.containers
    # for container in containers:
    #     for env in scenario["envs"]:
    #         logger.info(f" env.name={env['name']}, env.value={env['value']}")
    #         container.env.append(client.V1EnvVar(name=env["name"], value=str(env["value"])))


    # api.replace_namespaced_deployment(
    #     name=deploy_name,
    #     namespace=namespace,
    #     body=deployment
    # )

    patch_body = [{"op": "add", "path": "/spec/template/spec/containers/0/env", "value": scenario["envs"]}]
    api.patch_namespaced_deployment(name=deploy_name, namespace=namespace, body=patch_body)

    # Set the resource requests and limits for the scenario
    logger.info(f"Setting resource requests and limits for scenario {scenario['scenario_name']}...")
    patch_body = [{"op": "add", "path": "/spec/template/spec/containers/0/resources", "value": scenario["resources"]}]
    api.patch_namespaced_deployment(name=deploy_name, namespace=namespace, body=patch_body)
    logger.info("after patch_body wait for 30 seconds to enable the new pods")
    time.sleep(30)
   
    # delete the pod in the deployment 
    # pod_template_spec = deployment.spec.template
    # pod_list = core_api.list_namespaced_pod(namespace, label_selector=f"app={app_name}")

    # for pod in pod_list.items:
    #     logger.info(f"Will delete the pod: {pod.metadata.name} ...")
    #     core_api.delete_namespaced_pod(pod.metadata.name, namespace)
    # logger.info(f"Finished delete all the pod of deploy: {deploy_name} in scenario: {scenario['scenario_name']}")

    # Wait for the pods to be ready
    logger.info(f"Waiting for {deployment.spec.replicas} pods to be ready for scenario {scenario['scenario_name']}...")
    start_time = time.time()
    pods_ready = False

    pods = core_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={app_name}")
    #pprint(pods)
    # for p in pods.items:
    #     logger.info(f"pod: {p.metadata.name} status:{p.status.phase}")


    while not pods_ready:
        ready_pods =[]
        notready_pods =[]
        pods = core_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={app_name}")
        for p in pods.items:
            logger.info(f"pod: {p.metadata.name} status:{p.status.phase}")
            if p.status.phase == "Running" and p.status.conditions[-1].status == "True":
                ready_pods.append(p)
                # logger.info(f"ready_pods.append :{p.metadata.name}")
            else:
                notready_pods.append(p)    
                # logger.info(f"notready_pods.append :{p.metadata.name}")
        #ready_pods = [pod for pod in pods.items if pod.status.phase == "Running" and pod.status.conditions[-1].status == "True"]
        if len(ready_pods) == deployment.spec.replicas and len(notready_pods) ==0:
            logger.info(f"All {deployment.spec.replicas} pods are ready for scenario {scenario['scenario_name']}")
            pods_ready = True
        else:
            waiting_for = deployment.spec.replicas - len(ready_pods)
            elapsed_time = time.time() - start_time
            remaining_pods = deployment.spec.replicas - len(ready_pods)
            logger.info(f"Waiting for {waiting_for} more pods to be ready, there are {len(notready_pods)} not ready pods for scenario {scenario['scenario_name']}. Elapsed time: {elapsed_time:.2f} seconds")
            time.sleep(10)




def init_logger(log_file):
    # Configure logging to file and console
    logger = logging.getLogger('batch_deploy')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Log to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Starting batch deployment...")
    return logger


def test_create_deploy():
    # kubectl create deployment my-dep --image=nginx --replicas=3
    developments = ['dev1', 'dev2', 'dev3']

    for dev in developments:
        # Create the development
        create_dev_command = ['kubectl', 'create', 'deployment', dev,'--image=nginx','--replicas=10']
        subprocess.run(create_dev_command, check=True)
        logger.info(f"after create_dev_command, deveployment: {dev}")
        # Wait for all the pods to be ready

        rollout_command = ['kubectl', 'rollout', 'status', f'deployment/{dev}']
        logger.info(f"before rollout_command, deveployment: {dev}")
        #subprocess.run(rollout_command, check=True)
        process = subprocess.Popen(rollout_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stdout:
            logger.info(line.strip())
        logger.info(f"finish rollout_command, deveployment: {dev}")



        
        # Continue with other tasks once all pods are ready
        print(f"All pods are ready for {dev}. Continuing with other tasks...")

if __name__ == "__main__":
    # Define a prefix
    r = lambda: random.randint(0,255)
    prefix = '%02X%02X_' % (r(),r())
    print("prefix="+prefix)
    
    logger = init_logger("batch_deploy_bench.log")
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="default", help="the namespace of the deployment")
    parser.add_argument("--deploy_name", default="ei-infer-deployment-pose-bf16-amx-01", help="the name of the deployment")
    parser.add_argument("--app_name", default="ei-infer-pose-bf16-amx-app", help="the name of the app name")
    parser.add_argument("--config_file", default="scenarios.json", help="the path to the scenarios config file")
    args = parser.parse_args()

    # test_create_deploy()
    # sys.exit(0)


    # Load the scenarios from the config file
    with open(args.config_file) as f:
        scenarios = json.load(f)

    # Iterate over the scenarios and set the deployment env
    i = 0
    for scenario in scenarios:
        i = i + 1
        logger.info(f"------------- scenario: {i}/{len(scenarios)} ------------")
        logger.info(f"Begin set_deployment_env of scenario : {scenario['scenario_name']} ...")
        set_deployment_env(args.namespace, args.deploy_name, args.app_name, scenario)
        logger.info(f"Finished scenario {scenario['scenario_name']}")

        # wait for 2m to get stable metrics
        logger.info(f"wait for 2m to get stable metrics ...")
        time.sleep(120)

        # Call the benchmarking script
        logger.info(f"Running benchmarking script for scenario {scenario['scenario_name']}...")
        #subprocess.run([f"./loop_benchmarking.sh", f"{prefix}{scenario['scenario_name']}"])


        process = subprocess.Popen(["./loop_benchmarking.sh", f"{prefix}{scenario['scenario_name']}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stdout:
            logger.info(line.strip())
        # try:
        #     output = subprocess.check_output(["./loop_benchmarking.sh", f"{prefix}{scenario['scenario_name']}"], shell=True)
        #     logging.info(output.decode('utf-8'))
        # except subprocess.CalledProcessError as e:
        #     logging.error(e.output.decode('utf-8'))

    logger.info("Finished running all scenarios!")
