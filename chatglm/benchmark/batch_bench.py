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
prompt = "Once upon a time, there existed a little girl who liked to have adventures. She wanted to go to places and meet new people, and have fun"
#prompt = "please finish the story: Once upon a time, there existed a little girl who liked to have adventures and fun."
iterations = 3
# Set the list of CPU values you want to apply
#cpu_values = [1, 2, 4, 8, 16,24,32,40,48,56,64,72,80,88]
cpu_values = [112]
flag_cpum = 0

def cpu_seq(step,max_cpu):
  end = max_cpu-4
  increment = step

  #sequence = [1]  # Start the sequence with 1
  sequence = []
  current_number = 0
  while current_number + increment <= end:
    current_number += increment
    sequence.append(current_number)

  print(sequence)
  return sequence

def modify_deployment_resources(deployment_name, cpu_value, cmd):
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
    if cmd.strip():
        cmd_array = cmd.split()
        deployment.spec.template.spec.containers[0].command = cmd_array
    else:
        logger.info(f"Skipping empty command: {cmd}")


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

def do_bench(cpu_value,round,prompt):
    # Run the curl command
    logger.info(f"prompt={prompt}")
    logger.info(f"wait for {wait_seconds}")
    time.sleep(wait_seconds)  # Wait for 5 seconds after deployment completion
    logger.info(f"after time sleep, now send request to service")
    start_metrics_job(cpu_value,round)
    curl_command = (
      	'curl -s -X POST "http://172.16.28.100:30021/v1/completions" '
    	'-H \'Content-Type: application/json\' '
   	 	'-d \'{{"prompt": "{}", "history": []}}\''
    ).format(prompt)
 
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
    stop_metrics_job()


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

def get_pid_from_file():
    input_file_name = 'llm.pid'
    llm_pid=""

    try:
        # Open and read the content of the input file
        with open(input_file_name, 'r') as input_file:
            llm_pid = input_file.read()


    except FileNotFoundError:
        print(f"'{input_file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return llm_pid



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

def get_metrics():
    # getPid
    logger.info("get Pid")
    do_shell(f"./getPids.sh {flag_cpum}")
    llm_pid = get_pid_from_file()
    logger.info(f"llm_pid =  {llm_pid} ")
    
    # set RDT
    logger.info("set RDT pid for monitoring memory bandwidth ")
    do_shell(f"./rdtPids.sh {flag_cpum}")

    # run job
    logger.info("run job")

    
def start_metrics_job(cpu,round):
    logger.info("start metrics job")
    do_shell(f"./getPids.sh {flag_cpum}")
    llm_pid = get_pid_from_file()
    logger.info(f"llm_pid =  {llm_pid} ")

   
    extra_vars = {
        "LOG_PATH": "mtr_"+TS+"_c"+str(cpu)+"_r"+str(round),
        "PIDS": llm_pid
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
        "run_job",
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

import math

def generate_numa_commands(max_cpu=96, step=8):
    i00 = max_cpu//4
    i01 = 2*max_cpu//4 
    i10 = 3*max_cpu//4
    i11 = max_cpu-4
    
    n00 = max_cpu//4-1
    n01 = 3*max_cpu//4-1
    n10 = 2*max_cpu//4-1 
    n11 = max_cpu-1
    
    current_cpu = 0
    numa_command = ""
    commands = []
    #numa_command = f"/usr/bin/numactl -C 1 python3 llm_inference_api.py"
    #commands.append(numa_command)
    while current_cpu < max_cpu:
        current_cpu += step
        
        if current_cpu == 0:
            numa_command = f"/usr/bin/numactl -C 1"
        elif current_cpu <= i00:
            numa_command = f"/usr/bin/numactl -C 0-{current_cpu-1}"
        elif current_cpu <= i01:
            numa_command = f"/usr/bin/numactl -C 0-{n00},{i01}-{current_cpu+i00-1}" 
        elif current_cpu <= i10:
            numa_command = f"/usr/bin/numactl -C 0-{n00},{i01}-{n01},{i00}-{current_cpu-i00-1}"
        elif current_cpu <= i11:
            numa_command = f"/usr/bin/numactl -C 0-{n00},{i01}-{n01},{i00}-{n10},{i10}-{current_cpu-1}"
        else:
            break
        numa_command = numa_command + " python3 llm_inference_api.py"
        commands.append(numa_command)    
        print(numa_command)
        
    return commands

def generate_numa01_commands(max_cpu=96, step=8):
    i00 = max_cpu//4
    i01 = 2*max_cpu//4 
    i10 = 3*max_cpu//4
    i11 = max_cpu-4
    
    n00 = max_cpu//4-1
    n01 = 3*max_cpu//4-1
    n10 = 2*max_cpu//4-1 
    n11 = max_cpu-1
    
    current_cpu = 0
    numa_command = ""
    commands = []
    #numa_command = f"/usr/bin/numactl -C 1 python3 llm_inference_api.py"
    #commands.append(numa_command)
    while current_cpu < max_cpu:
        current_cpu += step
        cpu_cores = current_cpu // 2
        
        if cpu_cores == 0:
            numa_command = f"/usr/bin/numactl -C 1"
        elif cpu_cores <= i00:
            numa_command = f"/usr/bin/numactl -C 0-{cpu_cores-1},{i00}-{i00+cpu_cores-1}"
        elif cpu_cores <= i01 -2 :
            offset = cpu_cores - i00 - 1
            numa_command = f"/usr/bin/numactl -C 0-{n00},{i00}-{n10},{i01}-{i01+offset},{i10}-{i10+offset}" 
        else:
            break
        numa_command = numa_command + " python3 llm_inference_api.py"
        commands.append(numa_command)    
        print(numa_command)
        
    return commands
    
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
    parser.add_argument("--log_file", '-l',type=str, default="./batch_bench.log", help="log file name")
    parser.add_argument("--iter", '-t',type=int, default=3, help="iterations default:3")
    parser.add_argument("--cpu_max", '-m',type=int, default=224, help="cpu max number")
    parser.add_argument("--cpu_step", '-s',type=int, default=8, help="cpu value step")
    parser.add_argument("--cpu_index", '-i',type=int, default=0, help="define cpu value ")  
    parser.add_argument("--prompt", '-p',type=str, help="prompt string")
    parser.add_argument("--cpu_manager", '-c',type=int, required=True, default=0, help="check if use cpu_manager 0:NO 1:YES default=0")
    parser.add_argument("--numa_order", '-n',type=int, required=True, default=0, help="numa order  0:numa0->numa1 1:numa0+numa1 default=0")
    parser.add_argument('--dry-run', action='store_true', help='Run the script in dry-run mode.')

    args = parser.parse_args()
    logger = init_logger(args.log_file+"."+timestamp)
    logger.info(f'the arguments: {args}')

    # print critical info
    if args.numa_order == 0:
        commands = generate_numa_commands(args.cpu_max,args.cpu_step)
    else:
        commands = generate_numa01_commands(args.cpu_max,args.cpu_step)

    logger.info(f"length of commands={len(commands)}")
    for cmd in commands:
        logger.info(cmd)
    cpu_values = cpu_seq(args.cpu_step,args.cpu_max)
    flag_cpum = args.cpu_manager
    logger.info(f"length of cpu_values={len(cpu_values)}")
    iterations=args.iter
    if not (args.prompt is None or args.prompt) :
        prompt = args.prompt


    if args.dry_run:
        logger.info(f'dry-run======>')
        #generate_numa01_commands(224,8)
        exit(0)
    
    
    deployment_name = "llm-deploy"  # Replace with your deployment name
    
    current_datetime = datetime.now()
    # Format the datetime object as a string
    TS = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")


    copy_script()



    # do_bench()
    # do_test()


    #i = 0
    for i,cpu_value in enumerate(cpu_values):
        logger.info(f"-------------------------")
        logger.info(f" deploy {deployment_name}: cpu={cpu_value}")

        if args.cpu_index in cpu_values:
            logger.info(f"args.cpu_index:{args.cpu_index} in cpu_values")
            if cpu_value != args.cpu_index:
                logger.info(f"cpu_value:{cpu_value} not meet args.cpu_index:{args.cpu_index}, continue")
                continue
            else:
                logger.info(f"cpu_value:{cpu_value}  meet args.cpu_index:{args.cpu_index}, will do this cpu_value")            
        else:
            logger.info(f"args.cpu_index:{args.cpu_index} not in cpu_values")

        #input("Before scale to 0, Press Enter to continue...")
        scale_deployment(0,deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After scale to 0, Press Enter to continue...")
        if flag_cpum == 1 : 
            modify_deployment_resources(deployment_name, cpu_value,"")
        else:
            modify_deployment_resources(deployment_name, cpu_value,commands[i])

        
        #wait_for_deployment_complete(deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After modify_deployment_resources, Press Enter to continue...")
        scale_deployment(1,deployment_name)
        wait_ready_deploy(deployment_name)
        #input("After scale to 1, Press Enter to continue...")
        get_metrics()
        for iteration in range(iterations):
            logger.info(f"Starting benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")
            do_bench(cpu_value,iteration,prompt)
            logger.info(f"Finished benchmark for CPU Value: {cpu_value}, Iteration: {iteration + 1}/{iterations}")

            

        

