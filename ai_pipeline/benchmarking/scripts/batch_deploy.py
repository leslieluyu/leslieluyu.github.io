import os
import argparse
import yaml
import logging
import subprocess
import time
from kubernetes import client, config

# Function to create a deployment from a YAML template with a given index
def create_deployment(infer_suffix, template_path, index):
    with open(template_path) as f:
        dep = yaml.safe_load(f)

    # logger.info(dep)

    # Update the deployment name with the index
    deploy_name = f"{dep['metadata']['name']}-deployment-{infer_suffix}"
    dep['metadata']['name'] = deploy_name

    # Update the label selector with the new deployment name
    # dep['spec']['selector']['matchLabels']['app'] = deploy_name
    # dep['spec']['template']['metadata']['labels']['app'] = deploy_name
    # dep['spec']['template']['spec']['containers'][0]['name'] = deploy_name
    

    # Update the environment variables with the index
    for container in dep['spec']['template']['spec']['containers']:
        for env in container['env']:
            if env['name'] == 'INFER_TYPE':
                env['value'] = infer_suffix
                break

    # Create the deployment
    apps_v1 = client.AppsV1Api()
    apps_v1.create_namespaced_deployment(
        body=dep, namespace="default")

    # Wait for the deployment finish
    wait_ready_deploy(deploy_name)

def wait_ready_deploy(deploy_name):
    rollout_command = ['kubectl', 'rollout', 'status', f'deployment/{deploy_name}']
    logger.info(f"before rollout_command, deveployment: {deploy_name}")
    #subprocess.run(rollout_command, check=True)
    process = subprocess.Popen(rollout_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stdout:
        logger.info(line.strip())
    logger.info(f"finish rollout_command, deveployment: {deploy_name}")


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
        process = subprocess.Popen([rollout_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stdout:
            logger.info(line.strip())
        logger.info(f"finish rollout_command, deveployment: {dev}")



        
        # Continue with other tasks once all pods are ready
        logger.info(f"All pods are ready for {dev}. Continuing with other tasks...")

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

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--template_path", '-t',type=str, required=True, help="Path to deployment YAML template")
    parser.add_argument("--infer_type", '-i',type=str, required=True, help="infer_type for the name of queues")
    parser.add_argument("--begin_num",'-b', type=int, default=1, help="Starting number for name suffixes of deployment and queue")
    parser.add_argument("--end_num", '-e',type=int, default=50, help="Ending number for name suffixes of deployment and queue")
    parser.add_argument("--log_file", '-l',type=str, default="batch_deploy.log", help="log file name")
    parser.add_argument('--dry-run', action='store_true', help='Run the script in dry-run mode.')
    args = parser.parse_args()
    logger = init_logger(args.log_file)

    logger.info(f'the arguments: {args}')
   
    # Load Kubernetes configuration
    config.load_kube_config()

    # Create the specified number of deployments
    for i in range(args.begin_num, args.end_num+1):
        infer_suffix = f"{args.infer_type}-q{i:02d}"
        if args.dry_run:
            logger.info(f'dry-run======> infer_suffix: {infer_suffix}, args.template_path:{args.template_path},index:{i}')
        else:
            logger.info(f'create_deployment=======> infer_suffix: {infer_suffix}, args.template_path:{args.template_path},index:{i}')
            create_deployment(infer_suffix, args.template_path, i)
            logger.info(f'after create_deployment wait 10 seconds ...')
            time.sleep(10)
            logger.info(f'10 seconds elapsed. ')
            
