import argparse
import subprocess
import time
import json
import logging
from datetime import datetime
from kubernetes import client, config
from pprint import pprint
import random
import sys



def get_deploy_by_pattern(pattern):
    logger.info(f"Pattern is : [{pattern}]")

    command = "kubectl get deployment | grep '{}' | awk '{{print $1}}'".format(pattern)
    logger.info(f"command is : {command}")
    output = subprocess.check_output(command, shell=True)

    # Convert the output to a list of strings
    deployments = output.decode().split()
    #logger.info(f"len os deployment is : {len(deployments)}")

    # Iterate over the list of deployments and do something with each one
    for deployment in deployments:
        # Do something with the deployment, for example print its name
        logger.info(f"|-deployment is : {deployment}")
    return deployments


def set_deployment_env(namespace, pattern, app_name, scenario):
    # Load the Kubernetes configuration and create the API client
    config.load_kube_config()
    api = client.AppsV1Api()
    core_api = client.CoreV1Api()


    deploys = get_deploy_by_pattern(pattern)   

    deployments = []
    # Iterate over the list of deployments and do something with each one
    for deploy_name in deploys:
        # Do something with the deployment, for example print its name
        logger.info(f"|-deployment is : {deploy_name}, begin to set env and resources")

        # Get the deployment object
        deployment = api.read_namespaced_deployment(name=deploy_name, namespace=namespace)
        deployments.append(deployment)
        # Set the environment variables for the scenario
        logger.info(f"Setting environment variables for scenario {scenario['scenario_name']}...")


        patch_body = [{"op": "add", "path": "/spec/template/spec/containers/0/env", "value": scenario["envs"]}]
        api.patch_namespaced_deployment(name=deploy_name, namespace=namespace, body=patch_body)
        # Set the resource requests and limits for the scenario
        logger.info(f"Setting resource requests and limits for scenario {scenario['scenario_name']}...")
        patch_body = [{"op": "add", "path": "/spec/template/spec/containers/0/resources", "value": scenario["resources"]}]
        api.patch_namespaced_deployment(name=deploy_name, namespace=namespace, body=patch_body)
    
    logger.info("after patch_body wait for 30 seconds to enable the new pods")
    time.sleep(30)
   

    
    # Wait for the pods to be ready
    logger.info(f"Waiting for {deployment.spec.replicas} pods to be ready for scenario {scenario['scenario_name']}...")
    start_time = time.time()
    pods_ready = False




    # Iterate over the list of deployments to wait all the pods of all deployments to be ready


    pods = core_api.list_namespaced_pod(namespace=namespace, label_selector=f"app={app_name}")


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


def confirm_selection():
    while True:
        user_input = input(f"Are you sure you want to continue? (y/n): ").lower()
        if user_input == "y":
            return True
        elif user_input == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    
    # Define a prefix
    r = lambda: random.randint(0,255)
    prefix = '%02X%02X_' % (r(),r())
    print("prefix="+prefix)
    
    logger = init_logger('batch_deploy_bench_multi_queue.log')
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="default", help="the namespace of the deployment")
    #parser.add_argument("--deploy_name", default="ei-infer-deployment-pose-bf16-amx-01", help="the name of the deployment")
    parser.add_argument("--deploy_pattern", '-p', default="ei-infer", required=True, help="the name pattern of the deployment")
    parser.add_argument("--app_name", default="ei-infer-pose-multi-queue-app", help="the name of the app name")
    parser.add_argument("--config_file", default="scenarios.json", help="the path to the scenarios config file")

    args = parser.parse_args()

    get_deploy_by_pattern(args.deploy_pattern)
    
    if not confirm_selection():
        sys.exit(0)

    # Load the scenarios from the config file
    with open(args.config_file) as f:
        scenarios = json.load(f)

    # Iterate over the scenarios and set the deployment env
    i = 0
    for scenario in scenarios:
        i = i + 1
        logger.info(f"------------- scenario: {i}/{len(scenarios)} ------------")
        logger.info(f"Begin set_deployment_env of scenario : {scenario['scenario_name']} ...")
        set_deployment_env(args.namespace, args.deploy_pattern, args.app_name, scenario)
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
