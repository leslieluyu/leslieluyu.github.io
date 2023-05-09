import os
import argparse
import yaml
import subprocess
import time
from kubernetes import client, config
from base import init_logger

# Function to create a deployment from a YAML template with a given index
def create_deployment(infer_suffix, template_path, infer_type):
    with open(template_path) as f:
        dep = yaml.safe_load(f)

    # logger.info(dep)

    # Update the deployment name with the infer_suffix
    deploy_name = f"{dep['metadata']['name']}-deployment-{infer_suffix}"
    dep['metadata']['name'] = deploy_name

    # Update the label selector with the new deployment name
    # dep['spec']['selector']['matchLabels']['app'] = deploy_name
    # dep['spec']['template']['metadata']['labels']['app'] = deploy_name
    # dep['spec']['template']['spec']['containers'][0]['name'] = deploy_name
    

    # Update the environment variables infer_type with the infer_type, stream_name with the infer_suffix
    for container in dep['spec']['template']['spec']['containers']:
        for env in container['env']:
            if env['name'] == 'INFER_TYPE':
                env['value'] = infer_type
            elif env['name'] == 'STREAM_NAME':
                env['value'] = infer_suffix

    # Create the deployment
    apps_v1 = client.AppsV1Api()
    apps_v1.create_namespaced_deployment(
        body=dep, namespace="default")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--template_path", '-t',type=str, required=True, help="Path to deployment YAML template")
    parser.add_argument("--infer_type", '-i',type=str, required=True, help="infer_type for the name of queues")
    parser.add_argument("--begin_num",'-b', type=int, default=1, help="Starting number for name suffixes of deployment in a  queue")
    parser.add_argument("--end_num", '-e',type=int, default=50, help="Ending number for name suffixes of deployment in a queue")
    parser.add_argument("--begin_q",'-bq', type=int, default=1, help="Starting number for name suffixes of queue")
    parser.add_argument("--end_q", '-eq',type=int, default=1, help="Ending number for name suffixes of queue")
    parser.add_argument("--log_file", '-l',type=str, default="../logs/batch_deploy_multi_queue.log", help="log file name")
    parser.add_argument('--dry-run', action='store_true', help='Run the script in dry-run mode.')
    args = parser.parse_args()
    logger = init_logger(args.log_file)

    logger.info(f'the arguments: {args}')
   
    # Load Kubernetes configuration
    config.load_kube_config()

    # Create the specified number of deployments
    for q in range(args.begin_q, args.end_q+1):
        for i in range(args.begin_num, args.end_num+1):
            infer_suffix = f"{args.infer_type}-q{q:02d}-r{i:02d}"
            infer_type = f"{args.infer_type}-q{q:02d}"
            if args.dry_run:
                logger.info(f'dry-run======> infer_suffix: {infer_suffix}, args.template_path:{args.template_path},queue:{q},replic:{i}')
            else:
                logger.info(f'create_deployment=======> infer_suffix: {infer_suffix}, args.template_path:{args.template_path},queue:{q},replic:{i}')
                create_deployment(infer_suffix, args.template_path, infer_type)
                logger.info(f'after create_deployment wait 10 seconds ...')
                time.sleep(10)
                logger.info(f'10 seconds elapsed. ')
