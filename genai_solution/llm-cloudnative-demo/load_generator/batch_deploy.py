from kubernetes import client, config
import argparse
import subprocess
import time
import logging
from base import init_logger
from datetime import datetime
import json

timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
wait_seconds=30
iterations = 7 
# Set the list of CPU values you want to apply
cpu_values = [1, 2, 4, 8, 16,24,32,40,48,56,64,72,80,88]

def modify_deployment_resources(deployment_name, cpu_value):
    config.load_kube_config()  # Load the Kubernetes config from the default location

    v1 = client.AppsV1Api()
    deployment = v1.read_namespaced_deployment(deployment_name, "default")

    # Modify CPU requests and limits
    container = deployment.spec.template.spec.containers[0]
    container.resources.requests["cpu"] = str(cpu_value)
    container.resources.limits["cpu"] = str(cpu_value)

    # Set OMP_NUM_THREADS
    container.env.append(client.V1EnvVar(name="OMP_NUM_THREADS", value=str(cpu_value)))

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


def process_result(result,extraInfo):
        response_data = json.loads(result)
        logger.info(f"{extraInfo} - Status: {response_data['status']}")
        logger.info(f"Total Duration: {response_data.get('total_dur', 'N/A')}")
        logger.info(f"Prompt Tokens: {response_data.get('prompt_tokens', 'N/A')}")
        logger.info(f"Completion Tokens: {response_data.get('completion_tokens', 'N/A')}")
        logger.info(f"Latency per Token: {response_data.get('latency_per_token', 'N/A')}")
        logger.info("\n")

def do_bench(cpu_value):
    # Run the curl command
    logger.info(f"wait for {wait_seconds}")
    time.sleep(wait_seconds)  # Wait for 5 seconds after deployment completion
    logger.info(f"after time sleep, now send request to service")
    curl_command = (
        'curl -s -X POST "http://llm.intel.com/v1/completions" '
        '-H \'Content-Type: application/json\' '
        '-d \'{"prompt": "What is AI?", "history": []}\''
    )
    
    # subprocess.run(curl_command, shell=True, check=True)
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # Read and print output line by line
    extraInfo = "CPU_Value=" + str(cpu_value)
    for line in process.stdout:
        result = line.strip()
        logger.info(line.strip())

    # Read and print error output line by line
    for line in process.stderr:
        logger.error(line.strip())

    # Wait for the process to complete
    process.wait()
    process_result(result,extraInfo)
    
def do_test():
    # Your JSON response string
    response_string = '{"status":200,"time":"2023-08-29 08:04:17","prompt":"What is AI?","history":[],"completion":"\\nAI stands for Artificial Intelligence. AI refers to the development of computer systems or software that can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.\\n\\nAI systems can be designed to perform a wide range of tasks, from simple and repetitive tasks to complex and creative tasks. They are often trained using large amounts of data and algorithms that allow them to learn and improve over time.\\n\\nSome examples of AI include voice recognition software, image and speech recognition software, and machine learning algorithms that can be used to analyze and predict data. AI has the potential to revolutionize many industries and make our lives easier and more efficient.","total_dur":34.8892924785614,"prompt_tokens":6,"completion_tokens":140,"latency_per_token":249.18270451681954}'

    # Parse the JSON response string
    response_data = json.loads(response_string)

    # Extract and print the desired values
    # status = response_data["status"]
    # status = response_data.get('status')
    # total_dur = response_data["total_dur"]
    # prompt_tokens = response_data["prompt_tokens"]
    # completion_tokens = response_data["completion_tokens"]
    # latency_per_token = response_data["latency_per_token"]

        # Extract and print the desired values with default values
    status = response_data.get('status', 'No Status')
    total_dur = response_data.get('total_dur', "N/A")
    prompt_tokens = response_data.get("prompt_tokens", 0)
    completion_tokens = response_data.get('completion_tokens', 0)
    latency_per_token = response_data.get('latency_per_token', 0.0)

    print("Status:", status)
    print("Total Duration:", total_dur)
    logger.info(f"Total Duration:{response_data.get('total_dur', 'N/A')}")
    print("Prompt Tokens:", prompt_tokens)
    print("Completion Tokens:", completion_tokens)
    print("Latency per Token:", latency_per_token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", '-l',type=str, default="./batch_deploy.log", help="log file name")
    args = parser.parse_args()
    
    logger = init_logger(args.log_file+"."+timestamp)
    deployment_name = "llm-deploy"  # Replace with your deployment name

    # do_bench()
    # do_test()
    # exit(0)


    for cpu_value in cpu_values:
        logger.info(f"-------------------------")
        logger.info(f" deploy {deployment_name}: cpu={cpu_value}")
        #input("Before scale to 0, Press Enter to continue...")
        scale_deployment(0,deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After scale to 0, Press Enter to continue...")
        modify_deployment_resources(deployment_name, cpu_value)
        #wait_for_deployment_complete(deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After modify_deployment_resources, Press Enter to continue...")
        scale_deployment(1,deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After scale to 1, Press Enter to continue...")
        for iteration in range(iterations):
            logger.info(f"Starting benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")
            do_bench(cpu_value)
            logger.info(f"Finished benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")
            

        

