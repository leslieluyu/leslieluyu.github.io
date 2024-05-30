import collections
import random
import string
import subprocess,argparse,yaml,re,time,json
import concurrent.futures
import requests
from kubernetes import client, config
from base import init_logger
from datetime import datetime, timedelta
from interval import Interval
 

def generate_random_string(length):
    # Define the characters you want to use
    characters = string.ascii_lowercase + string.digits  # You can add more characters if needed

    # Generate a random string of specified length
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
def get_uniq_log_suffix(TS):
    return TS+"_"+generate_random_string(4)

TS = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y%m%d%H%M%S")
TS_R = get_uniq_log_suffix(TS)

  
namespace = "default"  # Replace with your namespace
labels = "app=llm-deploy"  # Replace with your label selector
EXACT_LABEL = "exact_pod"

# Define the URL and payload data for the POST requests
url = "http://llm.intel.com/v2/completions"
#url = "http://172.16.28.100:30021/v1/completions"
prompt = "Once upon a time, there existed a little girl who liked to have adventures. She wanted to go to places and meet new people, and have fun"
prompt = "complete this: At daybreak the young hero embarked on a perilous journey through the misty vale. Wary of lurking beasts, he tread lightly over the damp earth. In the distance, a majestic castle loomed over the horizon. The lad hoped to find refuge there. As the sun rose over the hills, its brilliant rays illuminated the landscape. The dense fog began to dissipate, revealing a winding path. Cautious, the traveler gripped his walking stick and proceeded ahead. He soon arrived at a fork in the road. Unsure which route to take, he chose the path to the left. After some time, he came upon a babbling brook. The cool water looked inviting. Kneeling down to take a drink, he noticed tiny fish swimming along with the current. He watched them for a moment, then continued on. Before long, the trail became rocky and steep. Clambering over large boulders, he reached a sheer cliffside. There was no choice but to scale the precipice. Finding handholds in the rock face, he started to climb. It was arduous work. His muscles ached but he persevered, finally pulling himself up onto a ledge. He sat there catching his breath and gazed out at the vistas before him. In the far distance, he could make out the turrets of the castle. It gave him hope. With renewed vigor, the lad ventured upward. As the sun passed its zenith, he neared the summit. Glancing back, he saw how far he had come. Towering pines now looked diminutive from this height. Pressing forward, he pushed through waist-high drifts of snow. Icy winds nipped at his cheeks but could not deter him. At last he reached the top. An immense valley spread out below. Nestled within was the majestic castle, now close at hand. But the final stretch would prove the most perilous. Hugging the mountainside, he inched along a narrow outcropping with a precipitous drop. He dared not look down. The risk was great, but he trusted in his abilities. Inch by inch he traversed the ledge, finally reaching more stable ground. From there, it was a short hike to the castle gates. He arrived there exhausted but jubilant. The grand wooden doors slowly opened, and he was greeted by a friendly maiden. Welcome to our castle, brave lad, she said. Stay and rest here as long as you like. At last, he had found a sanctuary. His long journey was at an end."
prompt = "Continue this story no less than 1024 words: At daybreak the young hero embarked on a perilous journey through the misty vale. Wary of lurking beasts, he tread lightly over the damp earth. In the distance, a majestic castle loomed over the horizon. The lad hoped to find refuge there. As the sun rose over the hills, its brilliant rays illuminated the landscape. The dense fog began to dissipate, revealing a winding path. Cautious, the traveler gripped his walking stick and proceeded ahead. He soon arrived at a fork in the road. Unsure which route to take, he chose the path to the left. After some time, he came upon a babbling brook. The cool water looked inviting. Kneeling down to take a drink, he noticed tiny fish swimming along with the current. He watched them for a moment, then continued on. Before long, the trail became rocky and steep. Clambering over large boulders, he reached a sheer cliffside. There was no choice but to scale the precipice. Finding handholds in the rock face, he started to climb. It was arduous work. His muscles ached but he persevered, finally pulling himself up onto a ledge. He sat there catching his breath and gazed out at the vistas before him. In the far distance, he could make out the turrets of the castle. It gave him hope. With renewed vigor, the lad ventured upward. As the sun passed its zenith, he neared the summit. Glancing back, he saw how far he had come. Towering pines now looked diminutive from this height. Pressing forward, he pushed through waist-high drifts of snow. Icy winds nipped at his cheeks but could not deter him. At last he reached the top. An immense valley spread out below. Nestled within was the majestic castle, now close at hand. But the final stretch would prove the most perilous. Hugging the mountainside, he inched along a narrow outcropping with a precipitous drop. He dared not look down. The risk was great, but he trusted in his abilities. Inch by inch he traversed the ledge, finally reaching more stable ground. From there, it was a short hike to the castle gates. He arrived there exhausted but jubilant. The grand wooden doors slowly opened, and he was greeted by a friendly maiden. Welcome to our castle, brave lad, she said. Stay and rest here as long as you like. At last, he had found a sanctuary. His long journey was at an end. At daybreak the young hero embarked on a perilous journey through the misty vale. Wary of lurking beasts, he tread lightly over the damp earth. In the distance, a majestic castle loomed over the horizon. The lad hoped to find refuge there. As the sun rose over the hills, its brilliant rays illuminated the landscape. The dense fog began to dissipate, revealing a winding path. Cautious, the traveler gripped his walking stick and proceeded ahead. He soon arrived at a fork in the road. Unsure which route to take, he chose the path to the left. After some time, he came upon a babbling brook. The cool water looked inviting. Kneeling down to take a drink, he noticed tiny fish swimming along with the current. He watched them for a moment, then continued on. Before long, the trail became rocky and steep. Clambering over large boulders, he reached a sheer cliffside. There was no choice but to scale the precipice. Finding handholds in the rock face, he started to climb. It was arduous work. His muscles ached but he persevered, finally pulling himself up onto a ledge. He sat there catching his breath and gazed out at the vistas before him. In the far distance, he could make out the turrets of the castle. It gave him hope. With renewed vigor, the lad ventured upward. As the sun passed its zenith, he neared the summit. Glancing back, he saw how far he had come. Towering pines now looked diminutive from this height. Pressing forward, he pushed through waist-high drifts of snow. Icy winds nipped at his cheeks but could not deter him. At last he reached the top. An immense valley spread out below. Nestled within was the majestic castle, now close at hand. But the final stretch would prove the most perilous. Hugging the mountainside, he inched along a narrow outcropping with a precipitous drop. He dared not look down. The risk was great, but he trusted in his abilities. "
payload = {
    "prompt": f"{prompt}",
    "max_length":32,
    "history": []
}
headers = {
    "Content-Type": "application/json"
}
request_times = {}      
numactl_cmd = "/usr/bin/numactl -C "  
llm_cmd = "conda run --no-capture-output -n llmenv python api.py"
template_path = "../llm_deploy/llm_deploy_template.yaml"
service_file_path = "../llm_deploy/llm_service.yaml"
namespace = "default"
pattern = r'llm_pid=(\d+)'
llm_container_name = "llm-deploy-demo"
llm_deploy_name = "llm-deploy"
cpu_reserved = 4

def get_payload(input_prompt):
    payload = {
        "prompt": f"{input_prompt}",
        "max_length":32,
        "history": []
    }
    return payload
request_counter = 0  # 自增编号计数器

# Env Variable Name
NAME_OMP_NUM_THREADS = "OMP_NUM_THREADS"
NAME_LLAMA_CPP_THREADS = "LLM_SERVER_N_THREADS"
NAME_MODEL_NAME = "LLM_SERVER_MODEL_NAME"
NAME_MODEL_PATH = "LLM_SERVER_MODEL_PATH"
NAME_FRAMEWORK = "LLM_SERVER_BACKEND"
NAME_MODEL_DTYPE =  "LLM_SERVER_MODEL_DTYPE"
SCENARIO_COUNT = "scenario"
ARGUMENT_COUNT = "argument"


FILE_UNIQ_NAME = "mtr_"+TS_R+"_"+SCENARIO_COUNT



# 请求发送函数
def send_request(url, request_num,intput_payload=payload):
    # ram = random.randint(2, 3)
    # print(f"Request {request_num}: Wait for  random {ram} seconds")
    # time.sleep(ram)
    try:
        start_time = time.time()
        request_times[request_num] = start_time
        logger.info(f"Request {request_num} payload = {intput_payload}")
        logger.info(f"Request {request_num} started ...")
        response = requests.post(url, json=intput_payload, headers=headers, timeout=600)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        logger.info(f"response_data={response_data}")
        duration = time.time() - request_times.pop(request_num)
        logger.info(f"Request {request_num} took {duration:.2f} seconds")
        logger.info(f"Request {request_num} - Status:{response_data['status']}")
        logger.info(f"Total Duration:{response_data.get('total_dur_s', 'N/A')}")
        logger.info(f"Prompt Tokens:{response_data.get('prompt_tokens', 'N/A')}")
        logger.info(f"Completion Tokens:{response_data.get('completion_tokens', 'N/A')}")
        logger.info(f"Latency of Total Tokens:{response_data.get('total_token_latency_s', 'N/A')}")
        logger.info(f"Latency of First Token:{response_data.get('first_token_latency_ms', 'N/A')}")
        logger.info(f"Latency of Next Tokens:{response_data.get('next_token_latency_ms', 'N/A')}")
        logger.info(f"Latency per Token:{response_data.get('avg_token_latency_ms', 'N/A')}")
        logger.info(f"Request {request_num}: Get Response from {url}") #: {response.status_code}")
        logger.info("\n")
        return response_data

    except requests.RequestException as e:
         return f"Request {request_num}: Get Response from {url}: Error sending request to {url}: {e}"

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
        logger.info(f"Return Code: {return_code}")

        # Print the script's output (stdout and stderr)
        logger.info("Script Output:")
        logger.info(stdout.decode())
        logger.info(stderr.decode())

        # You can perform additional actions based on the return code here
        if return_code == 0:
            logger.info("Script executed successfully.")
        else:
            logger.info("Script execution failed.")

    except Exception as e:
        logger.info(f"Error: {str(e)}")

def do_ansible(command):

    try:
        # Run the Ansible playbook command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Check the return code and print the output
        if result.returncode == 0:
            logger.info("Ansible playbook executed successfully.")
        else:
            logger.info(f"Ansible playbook execution failed with return code {result.returncode}.")
        
        # Print the standard output and standard error
        if result.stdout:
            logger.info("Standard Output:")
            logger.info(result.stdout)
        if result.stderr:
            logger.info("Standard Error:")
            logger.info(result.stderr)
    except subprocess.CalledProcessError as e:
        logger.info(f"Ansible playbook execution failed with return code {e.returncode}.")
    except Exception as e:
        logger.info(f"An error occurred: {str(e)}")

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

    # Set OMP_NUM_THREADS & LLAMA_CPP_THREADS
    container.env.append(client.V1EnvVar(name=NAME_OMP_NUM_THREADS, value=str(cpu_value)))
    container.env.append(client.V1EnvVar(name=NAME_LLAMA_CPP_THREADS, value=str(cpu_value)))

    logger.info(f"CMD_STR:{CMD_STR}") 
    # Set the command
    if CMD_STR:
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


def wait_for_exact_pods_ready(deployment_name):
    config.load_kube_config()  # Load the Kubernetes config from the default location

    v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()
    
    
        # Wait for the pods to be ready
    deployment = v1.read_namespaced_deployment(deployment_name, "default")

    logger.info(f"Waiting for {deployment.spec.replicas} pods to be ready ...")
    start_time = time.time()
    pods_ready = False

    #pprint(pods)
    # for p in pods.items:
    #     logger.info(f"pod: {p.metadata.name} status:{p.status.phase}")
    exact_label = EXACT_LABEL + "="+deployment_name
    logger.debug(f"exact_label of pod in {deployment_name} is {exact_label}")

    while not pods_ready:
        ready_pods =[]
        notready_pods =[]
        
        pods = core_v1.list_namespaced_pod(namespace, label_selector=exact_label)
        
        for p in pods.items:
            logger.info(f"pod: {p.metadata.name} status:{p.status.phase}")
            if p.status.phase == "Running" and p.status.conditions[-1].status == "True":
                ready_pods.append(p)
                # logger.info(f"ready_pods.append :{p.metadata.name}")
            else:
                notready_pods.append(p)
                # logger.info(f"notready_pods.append :{p.metadata.name}")
        #ready_pods = [pod for pod in pods.items if pod.status.phase == "Running" and pod.status.conditions[-1].status == "True"]
        logger.debug(f"the pod info:{deployment_name}, All:{len(pods.items)},expect:{deployment.spec.replicas},Ready:{len(ready_pods)},NotReady:{len(notready_pods)}")
        if len(ready_pods) == deployment.spec.replicas and len(notready_pods) ==0:
            logger.info(f"All {deployment.spec.replicas} pods are ready !!!")
            pods_ready = True
        else:
            waiting_for = deployment.spec.replicas - len(ready_pods)
            elapsed_time = time.time() - start_time
            remaining_pods = deployment.spec.replicas - len(ready_pods)
            logger.info(f"Waiting for {waiting_for} more pods to be ready, there are {len(notready_pods)} not ready pods . Elapsed time: {elapsed_time:.2f} seconds")
            time.sleep(10)



def create_or_update_service(namespace, service_file_path):
    api_instance = client.CoreV1Api()
    with open(service_file_path) as f:
        service_manifest = yaml.safe_load(f)
    service_name = service_manifest['metadata']['name']

    try:
        api_instance.read_namespaced_service(name=service_name, namespace=namespace)
        logger.info(f"Service '{service_name}' already exists. Skipping creation.")
    except client.exceptions.ApiException as e:
        if e.status == 404:  # Service not found
            api_instance.create_namespaced_service(namespace=namespace, body=service_manifest)
            logger.info(f"Service '{service_name}' created successfully.")
        else:
            raise  # Raise other ApiException



def create_deployment(template_path, suffix=None,model_map=None):
    with open(template_path) as f:
        dep = yaml.safe_load(f)


    deploy_name = f"{dep['metadata']['name']}"

    # Update the deployment name with the index
    if  suffix:
        logger.info("The suffix is not empty:{suffix}")
        deploy_name = f"{dep['metadata']['name']}-{suffix}"
        dep['metadata']['name'] = deploy_name

    else:
        logger.info("The suffix is empty")

    logger.info(dep)
    
    if not model_map:
        logger.info("The model_map is empty")
    else:
        logger.info("The model_map is not empty")
        containers = dep['spec']['template']['spec']['containers']
        for container in containers:
            if container['name'] == llm_container_name:
                container_env = container.get('env', [])
                for env_var in container_env:
                    if env_var['name'] in model_map:
                        env_var['value'] = model_map[env_var['name']]

    exact_pod_label = dep['spec']['template']['metadata']['labels'].get(EXACT_LABEL)
    if exact_pod_label is not None:
        dep['spec']['template']['metadata']['labels'][EXACT_LABEL] = deploy_name


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

def generate_numactl_strings(cpu_max, instance_cpu):
    numactl_strings = []
    max_cores = cpu_max // 2
    cores_per_numa = max_cores // 2
    half_instance_cpu = instance_cpu // 2

    for i in range(0, cores_per_numa, half_instance_cpu):
        start_core = i
        end_core = min(i + half_instance_cpu, cores_per_numa)
        if end_core - start_core == half_instance_cpu:
            numa0 = f"{start_core}-{end_core - 1}"
            numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
            #numactl_string = f"/usr/bin/numactl --cpunodebind=0,1 --membind=0,1 --physcpubind={numa0},{numa1}  python3 llm_inference_api.py"
#            numactl_string = f"{numactl_cmd} {numa0},{numa1}  python3 llm_inference_api.py"
            numactl_string = f"{numactl_cmd} {numa0},{numa1}  {llm_cmd}"
            numactl_strings.append(numactl_string)

    return numactl_strings





def generate_numactl_str_multi_instance(cpu_max, instance_cpu,flag_ht,numa_order,max_instance):
    numactl_strings = []
    max_cores = cpu_max // 2
    cores_per_numa = max_cores // 2
    real_instance_cpu = instance_cpu
    if flag_ht == 0 and numa_order == 0:
        inst_core_used_in_numa = instance_cpu // 1
        real_instance_cpu = inst_core_used_in_numa
    elif (flag_ht == 0 and  numa_order == 1) or (flag_ht == 1 and numa_order == 0):
        inst_core_used_in_numa = instance_cpu // 2
        real_instance_cpu = 2 * inst_core_used_in_numa
    elif flag_ht == 1 and numa_order == 1:
        inst_core_used_in_numa = instance_cpu // 4
        real_instance_cpu = 4 * inst_core_used_in_numa
    else:
        inst_core_used_in_numa = 0
    
    
    logger.info(f"cores_per_numa:{cores_per_numa},instance_cpu:{instance_cpu},inst_core_used_in_numa:{inst_core_used_in_numa}")
    
    # for 1 instance
    if numa_order == 0:
        if flag_ht == 0:
            if instance_cpu > cores_per_numa:
                logger.info(f"instance1--- instance_cpu:{instance_cpu} > cores_per_numa:{cores_per_numa} ")
                cpu_in_each_block = instance_cpu // 2
                end_core = cpu_in_each_block
                start_core = 0
                numa0 = f"{start_core}-{end_core - 1}"
                numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
                numactl_string = f"{numactl_cmd} {numa0},{numa1}  {llm_cmd}"
                numactl_strings.append(numactl_string) 
        elif flag_ht == 1:
            if instance_cpu > max_cores:
                logger.info(f"instance1--- instance_cpu:{instance_cpu} > max_cores:{max_cores} ")
                cpu_in_each_block = instance_cpu // 4
                start_core = 0
                end_core = cpu_in_each_block
                numa0 = f"{start_core}-{end_core - 1}"
                numa0_ht = f"{start_core+max_cores}-{max_cores+end_core - 1}"
                numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
                numa1_ht = f"{max_cores+start_core + cores_per_numa}-{max_cores+end_core + cores_per_numa - 1}"
                numactl_string = f"{numactl_cmd} {numa0},{numa1},{numa0_ht},{numa1_ht}  {llm_cmd}"
                numactl_strings.append(numactl_string) 

             

    for index,val in enumerate(range(0, cores_per_numa, inst_core_used_in_numa)):
        #logger.info(f"index:{index},val:{val}")
        start_core = val
        end_core = min(val + inst_core_used_in_numa, cores_per_numa)
        # logger.info(f"start_core:{start_core},end_core:{end_core}")
        if end_core - start_core == inst_core_used_in_numa:
            if len(numactl_strings) >= max_instance and max_instance > 0 :
                logger.info(f"len(numactl_strings):{len(numactl_strings)} <= max_instance:{max_instance}. SO Break!!!!")
                break
            numa0 = f"{start_core}-{end_core - 1}"
            numa0_ht = f"{start_core+max_cores}-{max_cores+end_core - 1}"
            numa1 = f"{start_core + cores_per_numa}-{end_core + cores_per_numa - 1}"
            numa1_ht = f"{max_cores+start_core + cores_per_numa}-{max_cores+end_core + cores_per_numa - 1}"
            if flag_ht == 0 and numa_order == 0: 
                # logger.info(f"=== index:{index},value:{val},flag_ht:{flag_ht},numa_order:{numa_order},HT OFF and numa_order:numa0->numa1")
                numa0_str = f"{numactl_cmd} {numa0} {llm_cmd}"
                numa1_str = f"{numactl_cmd} {numa1} {llm_cmd}"
                numactl_strings.insert(index,numa0_str)
                numactl_strings.append(numa1_str)
            elif flag_ht == 0 and numa_order == 1:
                # logger.info(f"=== index:{index},value:{val},flag_ht:{flag_ht},numa_order:{numa_order},HT OFF and numa_order:numa0+numa1")
                numactl_string = f"{numactl_cmd} {numa0},{numa1}  {llm_cmd}"
                numactl_strings.append(numactl_string)
            elif flag_ht == 1 and numa_order == 0:
                # logger.info(f"=== index:{index},value:{val},flag_ht:{flag_ht},numa_order:{numa_order},HT ON and numa_order:numa0->numa1")
                numa0_str = f"{numactl_cmd} {numa0},{numa0_ht} {llm_cmd}"
                numa1_str = f"{numactl_cmd} {numa1},{numa1_ht} {llm_cmd}"
                numactl_strings.insert(index,numa0_str)
                numactl_strings.append(numa1_str)
            elif flag_ht == 1 and numa_order == 1:
                # logger.info(f"=== index:{index},value:{val},flag_ht:{flag_ht},numa_order:{numa_order},HT ON and numa_order:numa0+numa1")
                numactl_string = f"{numactl_cmd} {numa0},{numa1},{numa0_ht},{numa1_ht}  {llm_cmd}"
                numactl_strings.append(numactl_string) 

    return numactl_strings,real_instance_cpu


def get_cpu_ranges_orderly(num, ranges):

    count = 0 
    numa_string = ""
    for r in ranges:
        count_in_range = num - count
        if count_in_range <  len(r):
            numa_string = numa_string + f"{r.start}-{r.start+count_in_range - 1},"
            break
        else:
            numa_string = numa_string + f"{r.start}-{r.stop - 1},"
        count = count + len(r)
    numa_string = numa_string[:-1]
    
    return numa_string

def get_cpus_by_range(cpus,numa_ranges,distri_method):
    # distri_method:0 Evenly distribute cpus, 1: Orderly distriubte cpus
    cpus_string = ""
    logger.info(f"the cpus:{cpus},numa_ranges:{numa_ranges},distri_method:{distri_method} ")
    real_cpus = cpus
    if distri_method == 1:
        logger.info(f"Evenly distribute cpus...")
        cpus_per_range = cpus // len(numa_ranges)
        logger.info(f"cpus_per_range:{cpus_per_range}")
        real_cpus = cpus_per_range * len(numa_ranges)
        for r in numa_ranges:
            cpus_string = cpus_string + f"{r[0]}-{r[0]+cpus_per_range-1},"
        cpus_string = cpus_string[:-1]
        logger.info(f"Evenly cpus_string:{cpus_string}")
    elif distri_method == 0:
        logger.info(f"Orderly distriubte cpus...")
        cpus_string = get_cpu_ranges_orderly(cpus,numa_ranges)
        logger.info(f"Orderly cpus_string:{cpus_string}")

    else:
        logger.info(f"Do nothing...")
    return cpus_string,real_cpus
        


def generate_numactl_str_cpusets_commands(max_cpu=224, step=8,flag_ht=0,numa_order=0,llm_cmd=llm_cmd):
    current_cpu = 0
    commands = []
    cpu_nums = []

    max_cores = cpu_max // 2
    cores_per_numa = max_cores // 2

    r_n00 = range(0,cores_per_numa)
    r_n01 = range(cores_per_numa*2,cores_per_numa*3)
    r_n10 = range(cores_per_numa,cores_per_numa*2)
    r_n11 = range(cores_per_numa*3,cores_per_numa*4)

    ranges_NUMA01_HT0 = [r_n00,r_n10]
    ranges_NUMA01_HT1 = [r_n00,r_n01,r_n10,r_n11]
    ranges_NUMA0_HT1 = [r_n00,r_n01]
    ranges_NUMA1_HT1 = [r_n10,r_n11]
 
    max_cpu = (max_cores if flag_ht == 0 else max_cpu) - cpu_reserved
    current_cpu += step
    while current_cpu < max_cpu:
        if numa_order == 1 and flag_ht == 0:
            logger.info(f"numa_order:{numa_order} numa0+numa1, flag_ht:{flag_ht} HyperThreading OFF. Only evenly distributed in NUMA00,NUMA10")
            cpus_string,real_cpus = get_cpus_by_range(current_cpu,ranges_NUMA01_HT0,1)
        elif numa_order == 1 and flag_ht == 1:    
            logger.info(f"numa_order:{numa_order} numa0+numa1, flag_ht:{flag_ht} HyperThreading ON.  evenly distributed in NUMA00,NUMA01,NUMA10,NUMA11")
            cpus_string,real_cpus = get_cpus_by_range(current_cpu,ranges_NUMA01_HT1,1)
        elif numa_order == 0 and flag_ht == 0: 
            logger.info(f"numa_order:{numa_order} numa0+numa1, flag_ht:{flag_ht} HyperThreading OFF. Only orderly allocated in NUMA00,NUMA10")
            cpus_string,real_cpus = get_cpus_by_range(current_cpu,ranges_NUMA01_HT0,0)
        elif numa_order == 0 and flag_ht == 1:
            logger.info(f"numa_order:{numa_order} numa0+numa1, flag_ht:{flag_ht} HyperThreading OFF. Only orderly allocated in NUMA0,NUMA1, but need evenly in NUMA00,NUMA01 and in NUMA10,NUMA11")
            if current_cpu <= max_cores:
                logger.info("current_cpu:{current_cpu} <= half_of_max_cpus:{max_cores}. evenly distributed in NUMA0(NUMA00,NUMA01)")
                cpus_string,real_cpus = get_cpus_by_range(current_cpu,ranges_NUMA0_HT1,1)
            else:
                logger.info(f"current_cpu:{current_cpu} >= half_of_max_cpus:{max_cores}. evenly distributed the rest:{current_cpu - max_cores} in NUMA1(NUMA10,NUMA11) plus all numa00:{r_n00}+numa01:{r_n01}")
                cpus_string,real_cpus = get_cpus_by_range(current_cpu - max_cores,ranges_NUMA1_HT1,1)
                cpus_string = f"{r_n00[0]}-{r_n00[-1]},{r_n01[0]}-{r_n01[-1]}," + cpus_string
                real_cpus = real_cpus +  max_cores
        
        numactl_string = f"{numactl_cmd} {cpus_string} {llm_cmd}"
        commands.append(numactl_string) 
        cpu_nums.append(real_cpus)
        current_cpu += step
        logger.info(f"real_cpus:{real_cpus},cpus_string:{cpus_string}")
    logger.info(f"commands:{commands},cpu_nums:{cpu_nums}")
    return commands,cpu_nums

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
            logger.debug(f"pod.metadata.name={pod.metadata.name},pod.metadata.uid={pod.metadata.uid},pod.status.phase = {pod.status.phase},pod.status.container_statuses[0].ready={pod.status.container_statuses[0].ready}")
            if pod.status.phase == "Running" and pod.status.conditions[-1].status == "True":
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

    pids = []
    # Extract the specific value you need from the last line
    # pid_pattern = re.compile(r'llm_pid=(\d+)')
    int_pattern = re.compile(r'\d+')
    # matches = pid_pattern.findall(' '.join(output_lines))
    # pids = [int(pid) for pid in matches]
    if output_lines:
        logger.debug(f"llm pids output_lines={output_lines}")
        matched = False
        for line in output_lines:
            #logger.info(f"line:{line}")
            match = re.search(pattern, line)
            if match:
                logger.debug(f"matched and line:{line}")
                matched = True
                pid = match.group(1)
                logger.info(f"llm_pid={pid}")
                pids.append(pid)
            elif matched:
                int_match = re.search(int_pattern, line)
                logger.debug(f"matched and followed line:{line},int_match:{int_match}")
                pids.append(int(int_match.group(0)))
        logger.debug(f"pids={pids} before return...")
        return pids[-1]
    else:
        logger.info(f"the output_lines is empty!!! Can't get PID!!!")
        return None

def clear_rdt_mon_groups():
    # clear all the mon_groups in RDT
    logger.info("clear all the mon_groups in RDT")
    do_shell(f"./rdt_clear.sh")


def setPid_RDT_from_shell(pod_name,pid):
    # set RDT
    logger.info("set RDT pid for monitoring memory bandwidth ")
    do_shell(f"./rdtPids_multi_deploy.sh {pod_name} default {pid}")



def do_parse_response_to_map(response_data):
    try:
        # Parse the JSON
        json_dict = json.loads(json.dumps(response_data))

        # Create a map (dictionary) from the JSON fields and values
        result_map = {}

        for key, value in json_dict.items():
            result_map[key] = value

        # Print the result
        logger.debug(f"result_map === {result_map}")
        return result_map
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

def do_get_avg_from_maps(response_metrics_maps):
    prompt_tokens,completion_tokens,total_dur_s,total_token_latency_s,first_token_latency_ms,next_token_latency_ms,avg_token_latency_ms = 0,0,0,0,0,0,0
    l = len(response_metrics_maps)
    for result_map in response_metrics_maps:      
        prompt_tokens += result_map['prompt_tokens']
        completion_tokens += result_map['completion_tokens']
        total_dur_s += result_map['total_dur_s']
        total_token_latency_s += result_map['total_token_latency_s']
        first_token_latency_ms += result_map['first_token_latency_ms']
        next_token_latency_ms += result_map['next_token_latency_ms']
        avg_token_latency_ms += result_map['avg_token_latency_ms']
    
    prompt_tokens = prompt_tokens / l
    completion_tokens = completion_tokens / l
    total_dur_s = total_dur_s / l
    total_token_latency_s = total_token_latency_s / l
    first_token_latency_ms = first_token_latency_ms / l
    next_token_latency_ms = next_token_latency_ms / l
    avg_token_latency_ms = avg_token_latency_ms / l
    logger.info(f"The Average Metrics Value of Current Scenario is: {prompt_tokens:.2f},{completion_tokens:.2f},{total_dur_s:.2f},{total_token_latency_s:.2f},{first_token_latency_ms:.2f},{next_token_latency_ms:.2f},{avg_token_latency_ms:.2f} ")


# 主函数
def do_taffic(num_worker,iter,input_payload):
    # 要发送的请求的URL
    #url = "https://www.example.com"
    global request_counter
    #request_counter = 0  # 自增编号计数器
    max_workers =  num_worker # 最大线程数

    response_metrics_maps = []

    # 创建线程池，最多同时执行3个线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = set()
        #while True:
        for i in range(iter):
            logger.info(f"Current Max Workers of executor is  {executor._max_workers} workers...")
            logger.info(f"--- start the iteration:{i}")
            # 使用 for 循环确保初始时并发max_workers个请求
            for j in range(max_workers  - len(futures)):
                
                logger.info(f"Will submit iteration:{i},the {j} workers...")
                request_counter += 1  # 自增编号

                # 提交任务给线程池，实现并发发送请求，传入自增编号

                future = executor.submit(send_request, url, request_counter,input_payload)
                futures.add(future)

            while futures:
                # 使用 wait 等待任何一个请求完成
                done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                
                # 遍历完成的future
                failed_count = 0
                for future in done:
                    logger.info(" a future in done")
                    response_data = future.result()
                    logger.info(response_data)
                    response_metrics_maps.append(do_parse_response_to_map(response_data))
                    if "502 Server Error: Bad Gateway" in str(response_data):
    #                if response_data == "ERROR":
                        logger.info("Request failed")
                        failed_count = failed_count +1
                    else:
                        # 正常处理结果
                        logger.info("Request succeeded")
                

                # 移除已完成的请求
                futures.difference_update(done)
            logger.info(f"--- end the iteration:{i}\n")
            # # adjust the new size of threadpool
            # if failed_count > 0:
            #     print(f"There are {failed_count} failed request out of {max_workers} max requests!!!")
            #     max_workers =  max_workers - failed_count
            #     print(f"Let's adjusted the max thread count to new size {max_workers}")
            #     executor._max_workers = max_workers
            #     print(f"Finished adjusted the max thread count to new size {max_workers}")
            # logger.info("---\n---\n")
    do_get_avg_from_maps(response_metrics_maps)

def get_set_pids():
    pod_info = get_pod_info_by_labels(namespace, labels)
    pids=[]
    for info in pod_info:
        logger.info(f"Pod ID: {info['PodID']}, Container ID: {info['ContainerID']}, Deployment Name: {info['DeploymentName']}, Pod IP: {info['PodIP']}, Pod Name: {info['PodName']}")
        pid=getPid_from_shell(info['PodName'])
        pids.append(pid)
        if pid is not None:
            logger.info(f"Captured LLM PID: {pid}")
        else:
            logger.info("LLM PID not found in the output.")
        setPid_RDT_from_shell(info['PodName'],pid)
    return pids


def start_metrics_job(instance,round,scenario_folder_name):
    logger.info("clear the rdt mon groups")
    clear_rdt_mon_groups()
    
    logger.info("start metrics job")
    pids = get_set_pids()
    llm_pids = ",".join(map(str, pids))
    logger.info(f"pids_str={llm_pids}")
   
    extra_vars = {
        # "LOG_PATH": "mtr_"+TS_R+"_inst"+str(instance)+"_r"+str(round),
        "LOG_PATH": FILE_UNIQ_NAME,
        "PIDS": llm_pids,
        "scenario_folder_name": scenario_folder_name
    }

    # Convert the dictionary to a JSON string
    extra_vars_json = json.dumps(extra_vars)

    # Define the Ansible playbook command
    ansible_command = [
        "ansible-playbook",
        "-i",
        "hosts",
        "metric_jobs.yaml",
        "--tags",
        "run_job_multi",
        "--extra-vars",
        extra_vars_json
    ]
    do_ansible(ansible_command)

def stop_metrics_job():
    logger.info("stop metrics job")
    ansible_command = [
    "ansible-playbook",
    "-i",
    "hosts",
    "metric_jobs.yaml",
    "--tags",
    "get_jobid,stop_job"
    ]  
    do_ansible(ansible_command)

def do_delete_deploy():
    # -- delete deployment
    namespace = "default"  # Replace with your namespace
    labels = "app_deploy=llm-deploy-multi"  # Replace with your label selector

    deployments = list_deployments_by_labels(labels, namespace)

    if deployments:
        deployment_names = [deployment.metadata.name for deployment in deployments]
        delete_deployments(deployment_names, namespace)
    else:
        logger.info("No deployments matching the label selector found.")

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


    pod_info = get_pod_info_by_labels(namespace, labels)
    
    for info in pod_info:
        logger.info(f"Pod ID: {info['PodID']}, Container ID: {info['ContainerID']}, Deployment Name: {info['DeploymentName']}, Pod IP: {info['PodIP']}, Pod Name: {info['PodName']}")
        pid=getPid_from_shell(info['PodName'])
        if pid is not None:
            logger.info(f"Captured LLM PID: {pid}")
        else:
            logger.info("LLM PID not found in the output.")
        setPid_RDT_from_shell(info['PodName'],pid)
    return len(pod_info)

def test_create_deploy():
    do_delete_deploy()
    template_path = "../llm_deploy/llm_deploy_template.yaml"
    suffix = "00"
    model_map = {
        '': "chatglm2-6b",
        'FRAMEWORK': "bigdl-llm-transformers", #bigdl-llm-transformers
        'MODEL_DTYPE': "int4"
    }
    deploy_name = create_deployment(template_path,"",model_map)#,suffix,model_map)


def test_create_or_update_service():
    create_or_update_service(namespace,service_file_path)
    return     

def do_bench(iter,input_payload,scenario_folder_name=""):

        copy_script()        
        pod_info = get_pod_info_by_labels(namespace, labels)
        inst = len(pod_info)
        logger.debug(f"=======inst number:{inst}=======")
        logger.debug(f"------------payload : {input_payload}")
        start_metrics_job(inst,iter,scenario_folder_name)
        do_taffic(inst,iter,input_payload)
        stop_metrics_job()



def do_deploy(cpu_max, instance_cpu, flag_ht,numa_order,template_path,max_instance=0,env_map=None):
    # if flag_ht == 0 :
    #     numactl_strings = generate_numactl_strings(cpu_max, instance_cpu)
    #     inst_cpu = instance_cpu
    # else:
    #     numactl_strings = generate_numactl_strings_HT(cpu_max, instance_cpu)
    #     inst_cpu = instance_cpu * 2

    numactl_strings,real_instance_cpu = generate_numactl_str_multi_instance(cpu_max, instance_cpu,flag_ht,numa_order,max_instance)
    inst_cpu = real_instance_cpu
      
    for i, numactl_string in enumerate(numactl_strings):
        print(f"{i}: {numactl_string}")

    # -- create deployment
    deploy_names = []
    for i,command in enumerate(numactl_strings):
        # 1. create deployment
        suffix = f"{i:02d}"
        
        
        deploy_name = create_deployment(template_path,suffix,env_map)
        deploy_names.append(deploy_name)
        scale_deployment(0,deploy_name)
        wait_ready_deploy(deploy_name)
        # 2. update deployment
        modify_deployment_resources(deploy_name, inst_cpu,command)
        scale_deployment(1,deploy_name)
        # 3. wait for deployment
        wait_ready_deploy(deploy_name)

    for deploy_name in deploy_names:
        wait_for_exact_pods_ready(deploy_name)



def instance_seq(step,max_instance):
  end = max_instance
  increment = step
  logger.debug(f"end={end},increment={increment}")

  #sequence = [1]  # Start the sequence with 1
  sequence = []
  current_number = 0
  while current_number + increment <= end:
    current_number += increment
    if current_number % 2 == 0:
        sequence.append(current_number)
  sequence.insert(0,1)
  print(sequence)
  return sequence

# based on the input parameters: cpu_max to scale from 1 2 3 ... till reach the max instance num
def do_auto_scale(cpu_max,max_instance,flag_ht,numa_order,input_prompt,iter,env_map=None):
    logger.info(f"begin do auto scale ..........")
    
    #1. get instance sequence
    logger.info(f"  get instance sequence ..........")
    instances = instance_seq(2,max_instance)
    
    
    #2. interate all the instances [1,2,4....]
    for instances in instances:
        if flag_ht == 1:
            cpu_per_inst = (cpu_max - cpu_reserved) // instances
        else:
            cpu_per_inst = (cpu_max - cpu_reserved) // 2 // instances
        logger.info(f"    instance={instances} cpu_per_inst={cpu_per_inst}")
        #2.1 get numactr_stings for each instance setting
        # numactl_strings,real_instance_cpu = generate_numactl_strings_HT(cpu_max,cpu_per_inst,flag_ht,numa_order)
        # numactl_strings = numactl_strings[0:max_instance]
        # for i, numactl_string in enumerate(numactl_strings):
        #     logger.info(f"{i}: {numactl_string}, real_instance_cpu: {real_instance_cpu}")
        #2.2 delete previous deploy
        logger.info(f"  -- will do_delete_deploy")
        do_delete_deploy()
        logger.info(f"  -- will do_deploy cpu_max:{cpu_max},instance_cpu:{cpu_per_inst},flag_ht:{flag_ht},numa_order:{numa_order},template_path:{template_path}") 
        #2.3 deploy instances
        do_deploy(cpu_max, cpu_per_inst, flag_ht,numa_order,template_path,0,env_map)
        #2.4 do bench 
        logger.info(f"  -- will do_bench iter:{iter}")
        time.sleep(30)
        do_bench(iter,get_payload(input_prompt))
    logger.info(f"end do auto scale ..........")


# based on the input parameters: cpu_max,cpu_step,cpu_index to multi deploy single instance 
def do_scale_up_cpusets(cpu_max,cpu_step,cpu_index,flag_ht,numa_order,input_prompt,iter,deployment_name="llm-deploy",env_map=None,scenario_folder_name=""):
    logger.info(f"begin do multi deploy cpusets ..........")
    iterations=iter
    # get cpu values and commands
    # cpu_values = cpu_seq(cpu_step,cpu_max)
    #logger.info(f"length of cpu_values={len(cpu_values)}")
    commands = []
    commands,cpu_nums = generate_numactl_str_cpusets_commands(cpu_max,cpu_step,flag_ht,numa_order,llm_cmd)

    if args.dry_run:
        logger.info(f'dry-run======>')
        for cpu_value,command in zip(cpu_nums,commands):
            logger.info(f" cpu_value:{cpu_value},command:{command}")
        exit(0)

    logger.info(f"  -- will do_delete_deploy")
    do_delete_deploy()
    #TODO need to use deployment_name
    deploy_name = create_deployment(template_path,"",env_map)
    logger.debug(f"deploy_name:{deploy_name}")
    wait_for_deployment_complete(deploy_name)
    logger.debug(f"will sleep 30 seconds ... ")
    time.sleep(30)
    # wait_for_deployment_complete(deploy_name)

    for i,cpu_value in enumerate(cpu_nums):
        logger.info(f"-------------------------")
        logger.info(f" deploy {deployment_name}: cpu={cpu_value}")

        if cpu_index in cpu_nums:
            logger.info(f"cpu_index:{cpu_index} in cpu_values")
            if cpu_value != cpu_index:
                logger.info(f"cpu_value:{cpu_value} not meet cpu_index:{cpu_index}, continue")
                continue
            else:
                logger.info(f"cpu_value:{cpu_value}  meet cpu_index:{cpu_index}, will do this cpu_value")            
        else:
            logger.info(f"cpu_index:{cpu_index} not in cpu_values")

        #input("Before scale to 0, Press Enter to continue...")
        scale_deployment(0,deployment_name)
        wait_ready_deploy(deployment_name)

        modify_deployment_resources(deployment_name, cpu_value,commands[i])
        wait_ready_deploy(deployment_name)

        scale_deployment(1,deployment_name)
        wait_ready_deploy(deployment_name)
        wait_for_exact_pods_ready(deployment_name)

        logger.debug(f"will sleep 60 seconds ... for each cpu deploy")
        time.sleep(30)
        do_bench(iterations,get_payload(input_prompt),scenario_folder_name)
        wait_for_exact_pods_ready(deployment_name)
        # for iteration in range(iterations):
        #     logger.info(f"Starting benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")
            
        #     logger.info(f"Finished benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")
            


    
    logger.info(f"end do multi deploy cpusets ..........")

# based on the input parameters: instance_cpu,cpu_max,numa_order,hyperthreading to deploy multi instance at same time and benchmarking...
def do_scale_out_multi_instance(benchmark_type,cpu_max,instance_cpu,flag_ht,numa_order,input_prompt,iter,max_instance,model_map,scenario_folder_name=""):
    logger.info(f"begin do multi instance  ..........")

    if benchmark_type == 0:
        logger.info(f"+++ will do benchmark only. benchmark_type:{benchmark_type}")
        logger.info(f"  -- will do_bench iter:{iter}")
        do_bench(iter,get_payload(input_prompt),scenario_folder_name)
    elif benchmark_type == 1:
        logger.info(f"+++ will do deploy only. benchmark_type:{benchmark_type}")
        logger.info(f"  -- will do_delete_deploy")
        do_delete_deploy()
        logger.info(f"  -- will do_deploy cpu_max:{cpu_max},instance_cpu:{instance_cpu},flag_ht:{flag_ht},numa_order:{numa_order},template_path:{template_path}") 
        do_deploy(cpu_max, instance_cpu, flag_ht,numa_order,template_path,max_instance,model_map)
    elif benchmark_type == 2:
        logger.info(f"+++ will do deploy and benchmark. benchmark_type:{benchmark_type}")
        logger.info(f"  -- will do_delete_deploy")
        do_delete_deploy()
        logger.info(f"  -- will do_deploy cpu_max:{cpu_max},instance_cpu:{instance_cpu},flag_ht:{flag_ht},numa_order:{numa_order},template_path:{template_path}") 
        do_deploy(cpu_max, instance_cpu, flag_ht,numa_order,template_path,max_instance,model_map)
        logger.info(f"  -- will do_bench iter:{iter}")
        time.sleep(30)
        do_bench(iter,get_payload(input_prompt),scenario_folder_name)
    elif benchmark_type == 3:
        logger.info(f"+++ will do delete deploy only. benchmark_type:{benchmark_type}")
        logger.info(f"  -- will do_delete_deploy")
        do_delete_deploy()
    logger.info(f"end do multi instance  ..........")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", '-l',type=str, default="./multi_deploy.log", help="log file name")
    parser.add_argument("--model_name", '-n',type=str, default="chatglm2-6b", help="model name: chatglm2-6b or llama2-7b")
    parser.add_argument("--model_path", '-P',type=str, default="/models/chatglm2-6b", help="model path")
    parser.add_argument("--framework", '-f',type=str, default="transformers", help="model framework: transformers|bigdl-llm-transformers|openvino")
    parser.add_argument("--precision", '-p',type=str, default="fp16", help="model data precision: fp16|int8|int4|bf16")
    parser.add_argument("--scale_type", '-s',type=int, default=0, help="scale type 0:scale by params 1:autoscale 2:deploy cpus")
    parser.add_argument("--max_instance", '-x',type=int, default=224, help="the scaled instance number should <= max_instance")
    parser.add_argument("--scenario_info", '-o',type=str, required=True, help="Briefly describe the test scenario. no more than 12 chars")
    parser.add_argument("--scenario_file",type=str, help="read scenario setting from scenario_file, then benchmarking...")

    # for multi deploy cpusets
    parser.add_argument("--cpu_max", type=int, default=224, help="cpu max number")
    parser.add_argument("--cpu_step", type=int, default=8, help="cpu value step")
    parser.add_argument("--cpu_index", type=int, default=0, help="define cpu value ")  
    parser.add_argument("--cpu_reserved", type=int, default=4, help="reserved cpu not to be apply")
    # for mulit instances
    # parser.add_argument("--max_cores", '-m',type=int, default=112, help="core max number")
    parser.add_argument("--instance_cpu", '-c',type=int, default=16, help="cpus/threads each instance uses")
    parser.add_argument("--iteration", '-i',type=int, default=3, help="iteration count default:10")
    parser.add_argument("--hyperthreading", '-y',type=int, default=0, help="hyperthreading on/off 0:off 1:on default:0")
    parser.add_argument("--numa_order", '-r',type=int, default=0, help="numa order  0:numa0->numa1 1:numa0+numa1 default=0")
    parser.add_argument('--benchmark_type', '-t', type=int, default=0, help="0:only benchmark  1:deploy 2:deply+benchmark 3:only delete deploy")
    parser.add_argument('--dry_run', action='store_true', help='Run the script in dry-run mode.')
    args = parser.parse_args()



    return args
def test_inteval():
    N00 = Interval(0,55)
    logger.info(f"N00={N00},N00.count()={len(N00)}")


def test_get_cpus_by_range():
    cores_per_numa = 56
    r_n00 = range(0,cores_per_numa)
    r_n10 = range(cores_per_numa,cores_per_numa*2)
    r_n01 = range(cores_per_numa*2,cores_per_numa*3)
    r_n11 = range(cores_per_numa*3,cores_per_numa*4)
    rs_N1_HT0 = [r_n00,r_n10]
    rs_N1_HT1 = [r_n00,r_n01,r_n10,r_n11]
    rs_N0_HT0 = [r_n00,r_n10]
    print(f"rs_N1_HT0={rs_N1_HT0}")
    print(get_cpus_by_range(50,rs_N1_HT0,0))
    print(get_cpus_by_range(50,rs_N1_HT0,1))
    print(get_cpus_by_range(100,rs_N1_HT0,0))
    print(get_cpus_by_range(100,rs_N1_HT0,1))
    print(get_cpus_by_range(110,rs_N1_HT1,0))
    print(get_cpus_by_range(190,rs_N1_HT1,0))
    print(get_cpus_by_range(80,rs_N1_HT1,1))
    print(get_cpus_by_range(190,rs_N1_HT1,1))

    generate_numactl_str_cpusets_commands(224,8,0,1)
    generate_numactl_str_cpusets_commands(224,8,1,1)
    generate_numactl_str_cpusets_commands(224,8,0,0)
    generate_numactl_str_cpusets_commands(224,8,1,0)
    


def get_scenarios(scenario_file):
    with open(scenario_file) as f:
        data = json.load(f)

    prompt_map = {k: v for k, v in data['prompts'].items()}

    params = []
    print(f"------len of data['scenarios']={len(data['scenarios'])}")
    for scenario in data['scenarios']:
        # logger.info(f"scenario:{scenario}")
        print(f"scenario:{scenario}")
        model_params = []
        scenario_params = {
            'name': scenario.get('name'),
            # 'models': model_params,
            'cores': scenario.get('max_cores'),
            'iteration': scenario.get('iteration'),
            'numa_order': scenario.get('numa_order'),
            'hyperthreading': scenario.get('hyperthreading'),
            "scale_type" : scenario.get('scale_type'),
            "benchmark_type" : scenario.get('benchmark_type'),
            "cpu_max" : scenario.get('cpu_max'),
            "cpu_step" : scenario.get('cpu_step'),
            "cpu_index" : scenario.get('cpu_index'),
            "max_instance" : scenario.get('max_instance'),
            "instance_cpu" : scenario.get('instance_cpu'),
            'prompts': [{k: prompt_map[k]} for k in scenario['prompt_keys']]
        }
        for model in scenario['model_maps']:
            print(f"------ model:{model}")
            
            model_params = ({
            'name': model['MODEL_NAME'],
            'path': model['MODEL_PATH'],
            'framework': model['FRAMEWORK'], 
            'dtype': model['MODEL_DTYPE']
            })
            scenario_params['model_map']=model_params
            
            # logger.info(f"prompts:{scenario_params['prompts']}")
            for prompt in scenario_params['prompts']:
                # logger.info(f"prompt:{prompt}")
                prompt_name = list(prompt.keys())[0]
                scenario_params.update({'prompt_name':prompt_name})
                prompt_value = prompt[prompt_name]
                scenario_params.update({'prompt_value':prompt_value})
                # logger.info(f"before params.append scenario_params={scenario_params}")
                # logger.info(f"scenario_params.get('model_map')={scenario_params.get('model_map')}")
                # logger.info(f"scenario_params={scenario_params}")
                local_params = scenario_params.copy()
                params.append(local_params)
                
            #     params.append(prompt_m)
                
            # for k,v in enumerate(scenario['prompts']):
            #     scenario_params['prompt']={k:v}
    
    
    # for param in params:
    #     logger.info(f"before return params: param={param}")
    return params

def print_params(param):
    # logger.info(f"=======param:{param}")
    Printable_KEYS = ['name','cores','iteration','scale_type','numa_order','cpu_index','hyperthreading','prompt_name','model_map'] #'prompt_value'
    info = ""
    for key in Printable_KEYS:
        # logger.info(f"key:{key},value:{param[key]}")
        info = info + f"{key}: {param.get(key)} "
    logger.info(f" ++++++++= info={info}" )

def get_folder_by_scenario(scenario_param,scenario_index):

    #{'name': 'llama2-7b', 'path': '/models/llama2-7b-ov-int8', 'framework': 'openvino', 'dtype': 'int8'} 
    folder_name = str(scenario_index).zfill(3)+"_"+scenario_param.get("model_map").get("name") \
        +"_"+scenario_param.get("model_map").get("framework")+"_"+ scenario_param.get("model_map").get("dtype") \
        +"_scale_type"+str(scenario_param.get("scale_type"))+"_iter"+str(scenario_param.get("iteration")) \
        +"_prompt"+scenario_param.get("prompt_name")
    return folder_name

def write_FILE_NAME(FILE_UNIQ_NAME):
    output = open('./FILE_UNIQ_NAME', 'w') 
    output.write(FILE_UNIQ_NAME)      #把字符串S写入文件 
    output.close()

def test_get_scenarios():
    #scenario_file = "./scenarios.json"
    params = get_scenarios(scenario_file)

    for i,param in enumerate(params):
        logger.debug(f"=============== the {i+1}/{len(params)} scenario info ===============")
        logger.debug(f"print with prompt:{param}")
        # logger.debug(f"param={param}")

        print_params(param)
        #logger.debug(f"the {i} param:{param}")
    
def test_get_pod():
    config.load_kube_config()  # loads local kube config file
    v1 = client.CoreV1Api()
    
    # List all pods in the 'default' namespace
    ret = v1.list_namespaced_pod(namespace="default")

    for pod in ret.items:
        print(f"Pod Name: {pod.metadata.name}")
        print(f"Pod Status: {pod.status.phase}")
        print("--------------")    

def test_get_pids():
    pod_name="llm-deploy-7b8f7c4884-p9nxj"
    getPid_from_shell(pod_name) 

def test_do_parse_response_to_map():
    response_data = {
        "status": 200,
        "prompt": "the constitution provides a framework for the government of the country and establishes institutions powers and duties of various institutions",
        "completion": "of the government.\\nthe constitution provides a framework for the government of the country and establishes institutions powers and duties of various institutions of the government. the constitution",
        "prompt_tokens": 22,
        "completion_tokens": 32,
        "total_dur_s": 4.966998174786568,
        "total_token_latency_s": 4.964238564483821,
        "first_token_latency_ms": 290.9704176709056,
        "next_token_latency_ms": 150.7505853810618,
        "avg_token_latency_ms": 155.13245514011942
    }
    
    do_parse_response_to_map(response_data)

    int_x = 4
    float_y = 4.0
    logger.debug(f"{int_x:.2f},{float_y:.2f}")

def test_clear_rdt_mon_groups():
    clear_rdt_mon_groups()

def test_dryrun():
    # test_get_cpus_by_range()
    #test_get_pod()
    # test_get_scenarios()
    # test_get_pids()
    # test_get_pod_info()
    #exit(0)
    
    #generate_numa01_commands(224,8)

    # numactl_strings,real_instance_cpu = generate_numactl_strings_HT(args.cpu_max,instance_cpu,flag_ht,numa_order)
    # for i, numactl_string in enumerate(numactl_strings):
    #     logger.info(f"{i}: {numactl_string}, real_instance_cpu: {real_instance_cpu}")
    do_auto_scale(cpu_max,max_instance,flag_ht,numa_order,prompt,iter,model_map)
    #test_create_deploy()
    
    #test_return_from_shell()
    copy_script()

    
    pod_info = get_pod_info_by_labels(namespace, labels)
    inst = len(pod_info)
    test_get_pod_info()


    
if __name__ == "__main__":
    # ======= 0.init 
    # ========= 0.1 init the arguments
    args = parse_arguments()
    model_name = args.model_name
    model_path = args.model_path
    framework = args.framework
    precision = args.precision
    model_map = {
        NAME_MODEL_NAME: args.model_name,
        NAME_MODEL_PATH: args.model_path,
        NAME_FRAMEWORK: args.framework,
        NAME_MODEL_DTYPE: args.precision
    }


    scale_type = args.scale_type
    max_instance = args.max_instance
    scenario_info = args.scenario_info

    cpu_max = args.cpu_max
    cpu_step = args.cpu_step
    cpu_index = args.cpu_index
    cpu_reserved = args.cpu_reserved

    # max_cores = args.max_cores
    instance_cpu = args.instance_cpu
    iter = args.iteration
    flag_ht = args.hyperthreading
    numa_order = args.numa_order
    benchmark_type = args.benchmark_type

    request_counter = 0

    # ========= 0.2 if the scenario_file is not empty then parse the scenario parameters
    scenario_params = None
    if args.scenario_file:
        scenario_params = get_scenarios(args.scenario_file)
        scenario_file = args.scenario_file
        SCENARIO_COUNT = SCENARIO_COUNT+str(len(scenario_params)).zfill(3)
        FILE_UNIQ_NAME = "mtr_"+TS_R+"_"+SCENARIO_COUNT
    else:
        FILE_UNIQ_NAME = "mtr_"+TS_R+"_"+ARGUMENT_COUNT
    write_FILE_NAME(FILE_UNIQ_NAME)

    # ========= 0.3 init the logger
    logger = init_logger(FILE_UNIQ_NAME)
    logger.info(f'the logger info will be {args.log_file+"."+TS_R}')
    logger.info(f'the arguments: {args}')
    logger.info(f"======== will test the scenario:{scenario_info} ========")

    # ========= 0.4 init Load Kubernetes configuration
    config.load_kube_config()



    
    # ========= 1 dry_run ...
    if args.dry_run:
        logger.debug(f'dry-run======>')
        random_chars = generate_random_string(4)
        print(random_chars+f"...TS:{TS},TS_R:{TS_R}")
        # test_do_parse_response_to_map()
        # test_clear_rdt_mon_groups()
        print(f"\nFILE_UNIQ_NAME={FILE_UNIQ_NAME}") 
        test_get_scenarios()
        exit(0)
        # test_dryrun()
        # exit(0)
        # start_metrics_job(inst,4)

    #exit(0)

    # ========= 2 Begin Benchmarking    
    create_or_update_service(namespace, service_file_path) 

    if scenario_params:
        logger.info(f"+++ begin benchmarking based on scenario_params:")
        for i,scenario_param  in enumerate(scenario_params):
            scenario_folder_name = str(i+1).zfill(3)
            scenario_folder_name = get_folder_by_scenario(scenario_param,i+1)
            logger.info(f"+++ begin {i+1}/{len(scenario_params)} of the scenario, the scenario_folder_name:{scenario_folder_name}, the param is:")
            logger.info(f"..............print_params..............")
            print_params(scenario_param)
            scale_type = scenario_param.get('scale_type')
            benchmark_type = scenario_param.get('benchmark_type')
            cpu_max = scenario_param.get('cpu_max')
            cpu_step = scenario_param.get('cpu_step')
            cpu_index = scenario_param.get('cpu_index')
            
            instance_cpu = scenario_param.get("instance_cpu")
            iter = scenario_param.get("iteration")
            flag_ht = scenario_param.get("hyperthreading")
            numa_order = scenario_param.get("numa_order")
            max_instance = scenario_param.get("max_instance")
            prompt = scenario_param.get("prompt_value")
            logger.info(f"scenario_param.model_map = {scenario_param.get('model_map')}")
            sce_model_map = scenario_param.get('model_map')
            model_map = {
                NAME_MODEL_NAME: sce_model_map.get('name'),
                NAME_MODEL_PATH: sce_model_map.get('path'),
                NAME_FRAMEWORK: sce_model_map.get('framework'),
                NAME_MODEL_DTYPE: sce_model_map.get('dtype')
            }
            logger.info(f"+++ scale type={scale_type}")
            if scale_type == 0: # scale out  type 0:scale by params 
                logger.info(f"+++ will do scale out multi instances +++")
                if args.dry_run:
                    logger.debug(f'dry-run======>')
                    exit(0)
                do_scale_out_multi_instance(benchmark_type,cpu_max,instance_cpu,flag_ht,numa_order,prompt,iter,max_instance,model_map,scenario_folder_name)
            elif scale_type == 1: # 1:autoscale 
                logger.info(f"+++ will do auto scale +++")
                if args.dry_run:
                    logger.debug(f'dry-run======>')
                    exit(0)
                do_auto_scale(cpu_max,max_instance,flag_ht,numa_order,prompt,iter,model_map)
            elif scale_type == 2: # 2:deploy cpus 
                logger.info(f"+++ will do scale up for single instance +++")
                if args.dry_run:
                    logger.debug(f'dry-run======>')
                    exit(0)
                do_scale_up_cpusets(cpu_max,cpu_step,cpu_index,flag_ht,numa_order,prompt,iter,llm_deploy_name,model_map,scenario_folder_name)

            logger.info(f"+++ end of {i+1}/{len(scenario_params)} of the scenario")
            logger.info(f"\n\n\n")
            time.sleep(5)
        exit(0)

    else :
        logger.info(f"+++ begin benchmarking without scenario fiel, only based on arguments... scale type={scale_type}")
        if scale_type == 0: # scale out  type 0:scale by params 
            logger.info(f"+++ will do scale out multi instances +++")
            do_scale_out_multi_instance(benchmark_type,cpu_max,instance_cpu,flag_ht,numa_order,prompt,iter,max_instance,model_map)
        elif scale_type == 1: # 1:autoscale 
            logger.info(f"+++ will do auto scale +++")
            do_auto_scale(cpu_max,max_instance,flag_ht,numa_order,prompt,iter,model_map)
        elif scale_type == 2: # 2:deploy cpus 
            logger.info(f"+++ will do scale up for single instance +++")
            do_scale_up_cpusets(cpu_max,cpu_step,cpu_index,flag_ht,numa_order,prompt,iter,llm_deploy_name,model_map)

    
            

