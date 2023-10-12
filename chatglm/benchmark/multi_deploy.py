import re
import subprocess,argparse,yaml
from kubernetes import client, config
from base import init_logger
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def do_shell(script):
    script_path = script

    try:
        # Run the shell script
        process = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the script to complete and capture its return code
        return_code = process.wait()

        # Capture the stdout and stderr from the script (if needed)
        stdout, stderr = process.communicate()

        # Print the return code
        print(f"Return Code: {return_code}")

        # Print the script's output (stdout and stderr)
        print("Script Output:")
        print(stdout.decode())
        print(stderr.decode())

        # You can perform additional actions based on the return code here
        if return_code == 0:
            print("Script executed successfully.")
        else:
            print("Script execution failed.")

    except Exception as e:
        print(f"Error: {str(e)}")

def do_ansible(command):

    try:
        # Run the Ansible playbook command
        subprocess.run(command, check=True)
        print("Ansible playbook executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Ansible playbook execution failed with return code {e.returncode}.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def copy_script():
    logger.info("copy_script")
    # Define the Ansible playbook command as a list
    ansible_command = [
        "ansible-playbook",
        "-i",
        "hosts",
        "metric_jobs.yaml",
        "--tags",
        "copy_job"
    ]
    do_ansible(ansible_command)

def modify_deployment_resources(deployment_name, cpu_value, CMD_STR):
    config.load_kube_config()  # Load the Kubernetes config from the default location

    v1 = client.AppsV1Api()
    deployment = v1.read_namespaced_deployment(deployment_name, "default")

    # Modify CPU requests and limits
    container = deployment.spec.template.spec.containers[0]
    container.resources.requests["cpu"] = str(cpu_value)
    container.resources.limits["cpu"] = str(cpu_value)

    # Set OMP_NUM_THREADS
    container.env.append(client.V1EnvVar(name="OMP_NUM_THREADS", value=str(cpu_value)))
     
    # Set the command
    if CMD_STR.strip():
        cmd_array = CMD_STR.split()
        deployment.spec.template.spec.containers[0].command = cmd_array
    else:
        logger.info(f"Skipping empty command: {CMD_STR}")


    v1.patch_namespaced_deployment(
        name=deployment_name, namespace="default", body=deployment
    )
    logger.info("Deployment '{}' modified with CPU value: {}".format(deployment_name, cpu_value))


def scale_deployment(replicas,deploy_name):
    scale_command = ['kubectl', 'scale', f'deployment/{deploy_name}', f'--replicas={replicas}']
    logger.info(f"before scale, deveployment: {deploy_name} to replicas={replicas}")
    process = subprocess.Popen(scale_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stdout:
        logger.info(line.strip())
    logger.info(f"finish scale, deveployment: {deploy_name} to replicas={replicas}")

def wait_ready_deploy(deploy_name):
    rollout_command = ['kubectl', 'rollout', 'status', f'deployment/{deploy_name}']
    logger.info(f"before rollout_command, deveployment: {deploy_name}")
    #subprocess.run(rollout_command, check=True)
    process = subprocess.Popen(rollout_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stdout:
        logger.info(line.strip())
    logger.info(f"finish rollout_command, deveployment: {deploy_name}")

    
def wait_for_deployment_complete(deployment_name):
    config.load_kube_config()  # Load the Kubernetes config from the default location

    v1 = client.AppsV1Api()

    while True:
        deployment = v1.read_namespaced_deployment(deployment_name, "default")
        available_replicas = deployment.status.available_replicas
        replicas = deployment.spec.replicas

        if available_replicas is not None and available_replicas == replicas:
            logger.info(f"Deployment '{deployment_name}' is complete")
            break
        else:
            logger.info(f"Waiting for deployment '{deployment_name}' to complete...")
            time.sleep(10)

def create_deployment(suffix, template_path):
    with open(template_path) as f:
        dep = yaml.safe_load(f)



    # Update the deployment name with the index
    deploy_name = f"{dep['metadata']['name']}-{suffix}"
    dep['metadata']['name'] = deploy_name

    logger.info(dep)
    

    # Update the label selector with the new deployment name
    # dep['spec']['selector']['matchLabels']['app'] = deploy_name
    # dep['spec']['template']['metadata']['labels']['app'] = deploy_name
    # dep['spec']['template']['spec']['containers'][0]['name'] = deploy_name




    # Create the deployment
    apps_v1 = client.AppsV1Api()
    apps_v1.create_namespaced_deployment(
        body=dep, namespace="default")

    # Wait for the deployment finish
    wait_ready_deploy(deploy_name)
    return deploy_name



def list_deployments_by_labels(labels, namespace):
    v1 = client.AppsV1Api()

    deployment_list = v1.list_namespaced_deployment(namespace, label_selector=labels)

    return deployment_list.items

def delete_deployments(deployment_names, namespace):
    v1 = client.AppsV1Api()

    for deployment_name in deployment_names:
        try:
            v1.delete_namespaced_deployment(name=deployment_name, namespace=namespace)
            logger.info(f"Deployment {deployment_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            logger.info(f"Error deleting deployment {deployment_name}: {e}")


def cpu_seq(step,max_cpu):
  end = max_cpu
  increment = step

  #sequence = [1]  # Start the sequence with 1
  sequence = []
  current_number = 0
  while current_number + increment <= end:
    current_number += increment
    sequence.append(current_number)

  print(sequence)
  return sequence

def generate_numactl_strings(max_cores, instance_core):
    numactl_strings = []

    cores_per_numa = max_cores // 2
    half_instance_core = instance_core // 2

    for i in range(0, cores_per_numa, half_instance_core):
        start_core = i
        end_core = min(i + half_instance_core, cores_per_numa)
        if end_core - start_core == half_instance_core:
            numa0 = f"{start_core}-{end_core - 1}"
            numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
            #numactl_string = f"/usr/bin/numactl --cpunodebind=0,1 --membind=0,1 --physcpubind={numa0},{numa1}  python3 llm_inference_api.py"
            numactl_string = f"/usr/bin/numactl -C {numa0},{numa1}  python3 llm_inference_api.py"
            numactl_strings.append(numactl_string)

    return numactl_strings

def generate_numactl_strings_HT(max_cores, instance_core):
    numactl_strings = []

    cores_per_numa = max_cores // 2
    half_instance_core = instance_core // 2

    for i in range(0, cores_per_numa, half_instance_core):
        start_core = i
        end_core = min(i + half_instance_core, cores_per_numa)
        if end_core - start_core == half_instance_core:
            numa0 = f"{start_core}-{end_core - 1}"
            numa0_ht = f"{start_core+max_cores}-{max_cores+end_core - 1}"
            numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
            numa1_ht = f"{max_cores+start_core + cores_per_numa}-{max_cores+end_core + cores_per_numa - 1}"
            #numactl_string = f"/usr/bin/numactl --cpunodebind=0,1 --membind=0,1 --physcpubind={numa0},{numa1}  python3 llm_inference_api.py"
            numactl_string = f"/usr/bin/numactl -C {numa0},{numa1},{numa0_ht},{numa1_ht}  python3 llm_inference_api.py"
            numactl_strings.append(numactl_string)

    return numactl_strings

def get_deployment_name(pod, namespace):
    owner_references = pod.metadata.owner_references
    for ref in owner_references:
        if ref.kind == "ReplicaSet":
            replica_set_name = ref.name
            # Use AppsV1Api to get the ReplicaSet
            apps_v1 = client.AppsV1Api()
            replica_set = apps_v1.read_namespaced_replica_set(replica_set_name, namespace)
            # Check if the ReplicaSet has a Deployment owner
            owner_references_rs = replica_set.metadata.owner_references
            for rs_ref in owner_references_rs:
                if rs_ref.kind == "Deployment":
                    return rs_ref.name

    return ""

def get_pod_info_by_labels(namespace, labels):
    config.load_kube_config()
    core_v1 = client.CoreV1Api()

    pod_info = []

    config.load_kube_config()
    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    pod_info = []

    try:
        pod_list = core_v1.list_namespaced_pod(namespace, label_selector=labels)

        for pod in pod_list.items:
            pod_id = pod.metadata.uid
            container_id = pod.status.container_statuses[0].container_id.replace("containerd://", "")
            deployment_name = get_deployment_name(pod,namespace)
            pod_ip = pod.status.pod_ip
            pod_name = pod.metadata.name

            pod_info.append({
                "PodID": pod_id,
                "ContainerID": container_id,
                "DeploymentName": deployment_name,
                "PodIP": pod_ip,
                "PodName": pod_name  # Include the Pod name in the output
            })

    except Exception as e:
        logger.info(f"Error: {e}")

    return pod_info

def getPid_from_shell(pod_name):
    # Your shell command
    command = f"./getPids_multi_deploy.sh {pod_name} default"
    logger.info(f"command={command}")
    # Run the shell command and capture the output
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Read and print the output line by line
    output_lines = []
    for line in proc.stdout:
        output_lines.append(line.strip())
        print(line, end="")

    # Wait for the command to finish
    proc.wait()

    # Extract the specific value you need from the last line
    if output_lines:
        last_line = output_lines[-1]
        specific_value = last_line.split(' ')[-1]
        match = re.search(r'llm_pid=(\d+)', specific_value)
    
        if match:
            pid = match.group(1)
            return pid
        else:
            return None
def setPid_RDT_from_shell(pod_name,pid):
    # set RDT
    logger.info("set RDT pid for monitoring memory bandwidth ")
    do_shell(f"./rdtPids_multi_deploy.sh {pod_name} default {pid}")


def test_return_from_shell():
        # Your shell command
    command = "echo 'Hello, World!'"

    # Run the shell command and capture the output
    output = subprocess.check_output(command, shell=True, text=True)

    # Split the output into lines and get the last line
    lines = output.strip().split('\n')
    last_line = lines[-1]

    # Print the last line
    print("Last line:", last_line)

def test_get_pod_info():
    namespace = "default"  # Replace with your namespace
    labels = "app=llm-deploy"  # Replace with your label selector

    pod_info = get_pod_info_by_labels(namespace, labels)
    
    for info in pod_info:
        logger.info(f"Pod ID: {info['PodID']}, Container ID: {info['ContainerID']}, Deployment Name: {info['DeploymentName']}, Pod IP: {info['PodIP']}, Pod Name: {info['PodName']}")
        pid=getPid_from_shell(info['PodName'])
        if pid is not None:
            logger.info(f"Captured LLM PID: {pid}")
        else:
            logger.info("LLM PID not found in the output.")
        setPid_RDT_from_shell(info['PodName'],pid)

if __name__ == "__main__":
    max_cores = 112
    instance_core = 10




    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", '-l',type=str, default="./multi_deploy.log", help="log file name")
    parser.add_argument("--max_cores", '-m',type=int, default=112, help="core max number")
    parser.add_argument("--instance_core", '-c',type=int, default=16, help="core each instance use")
    parser.add_argument("--hyperthreading", '-y',type=int, default=0, help="hyperthreading on/off 0:off 1:on default:0")
    parser.add_argument('--dry_run', action='store_true', help='Run the script in dry-run mode.')
    args = parser.parse_args()
    logger = init_logger(args.log_file+"."+timestamp)
    logger.info(f'the arguments: {args}')

    # -- Load Kubernetes configuration
    config.load_kube_config()
     
    # -- init the arguments
    max_cores = args.max_cores
    instance_core = args.instance_core
    llm_deploy_name = "llm-deploy"
    flag_ht = args.hyperthreading


    if flag_ht == 0 :
        numactl_strings = generate_numactl_strings(max_cores, instance_core)
        inst_cpu = instance_core
    else:
        numactl_strings = generate_numactl_strings_HT(max_cores, instance_core)
        inst_cpu = instance_core * 2


    for i, numactl_string in enumerate(numactl_strings):
        print(f"{i}: {numactl_string}")
   
    # -- dry_run ...
    if args.dry_run:
        logger.info(f'dry-run======>')
        #generate_numa01_commands(224,8)
        # numactl_strings = generate_numactl_strings_HT(112,16)
        # for i, numactl_string in enumerate(numactl_strings):
        #     print(f"{i}: {numactl_string}")
        #test_return_from_shell()
        copy_script()
        test_get_pod_info()
        exit(0)
    #exit(0)


    # -- delete deployment
    namespace = "default"  # Replace with your namespace
    labels = "app=llm-deploy-multi"  # Replace with your label selector

    deployments = list_deployments_by_labels(labels, namespace)

    if deployments:
        deployment_names = [deployment.metadata.name for deployment in deployments]
        delete_deployments(deployment_names, namespace)
    else:
        print("No deployments matching the label selector found.")

    # -- create deployment
    for i,command in enumerate(numactl_strings):
        # 1. create deployment
        suffix = f"{i:02d}"
        template_path = "../llm_deploy/llm_deploy_only_metrics_int4.yaml"
        
        deploy_name = create_deployment(suffix,template_path)
        # 2. update deployment
        modify_deployment_resources(deploy_name, inst_cpu,command)
        # 3. wait for deployment
        wait_ready_deploy(deploy_name)
    
    # -- iterate all the pod of llm_deploy ips
    pod_info = get_pod_info_by_labels(namespace, labels)
    
    for info in pod_info:
        logger.info(f"Pod ID: {info['PodID']}, Container ID: {info['ContainerID']}, Deployment Name: {info['DeploymentName']}, Pod IP: {info['PodIP']}")
        getPid_from_shell({info['PodID']}, {info['ContainerID']})