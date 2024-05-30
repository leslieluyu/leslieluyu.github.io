import statistics
import subprocess,argparse,yaml,re,time,json
import concurrent.futures
import requests
from kubernetes import client, config
from base import init_logger
from datetime import datetime



def process_membw(LOG_MEMBW):
    # Define the log file path
    log_file_path = LOG_MEMBW

    # Define the regular expression pattern to match the needed lines
    pattern = r"(mem_bw_(0_local|0_total|1_local|1_total)):\s(\d+)\sMB"

    # Define thresholds for acceptable data (adjust these as needed)
    min_value = 1000  # Minimum acceptable value (e.g., 1 GB)
    max_value = 400000  # Maximum acceptable value (e.g., 100 GB)

    # Initialize dictionaries to store values for each metric
    mem_bw_0_local_values = []
    mem_bw_0_total_values = []
    mem_bw_1_local_values = []
    mem_bw_1_total_values = []
    data = {}
    data["mem_bw_0_local"] = []
    data["mem_bw_0_total"] = []
    data["mem_bw_1_local"] = []
    data["mem_bw_1_total"] = []
    
    # Read and process the log file line by line
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = re.search(pattern, line)
            if match:
                key, value = line.strip().split(': ')
                if key in ["mem_bw_0_local", "mem_bw_0_total", "mem_bw_1_local", "mem_bw_1_total"]:
                    value_in_mb = int(value.split(' ')[0])
                    #logger.info(f"line:{line} key={key},value={value},value_in_mb={value_in_mb}")
                    if min_value <= value_in_mb <= max_value:
                        data[key].append(value_in_mb)
                        logger.debug(f"value_in_mb:{value_in_mb} added")
                    else:
                        logger.debug(f"value_in_mb:{value_in_mb} not added")
                        pass

    # Calculate average and maximum values
    average_mem_bw_0_local = sum(data["mem_bw_0_local"]) / len(data["mem_bw_0_local"]) if len(data["mem_bw_0_local"]) > 0 else 0
    average_mem_bw_0_total = sum(data["mem_bw_0_total"]) / len(data["mem_bw_0_total"]) if len(data["mem_bw_0_total"]) > 0 else 0
    average_mem_bw_1_local = sum(data["mem_bw_1_local"]) / len(data["mem_bw_1_local"]) if len(data["mem_bw_1_local"]) > 0 else 0
    average_mem_bw_1_total = sum(data["mem_bw_1_total"]) / len(data["mem_bw_1_total"]) if len(data["mem_bw_1_total"]) > 0 else 0
    max_mem_bw_0_local = max(data["mem_bw_0_local"]) if len(data["mem_bw_0_local"]) > 0 else 0
    max_mem_bw_0_total = max(data["mem_bw_0_total"]) if len(data["mem_bw_0_total"]) > 0 else 0
    max_mem_bw_1_local = max(data["mem_bw_1_local"]) if len(data["mem_bw_1_local"]) > 0 else 0
    max_mem_bw_1_total = max(data["mem_bw_1_total"]) if len(data["mem_bw_1_total"]) > 0 else 0

    print(f"mem_bw_0_totals={data['mem_bw_0_total']}")
    print(f"mem_bw_1_totals={data['mem_bw_1_total']}")

    # Print the results
    print(f"Average mem_bw_0_local: {average_mem_bw_0_local} MB")
    print(f"Average mem_bw_0_total: {average_mem_bw_0_total} MB")
    print(f"Average mem_bw_1_local: {average_mem_bw_1_local} MB")
    print(f"Average mem_bw_1_total: {average_mem_bw_1_total} MB")
    print(f"Maximum mem_bw_0_local: {max_mem_bw_0_local} MB")
    print(f"Maximum mem_bw_0_total: {max_mem_bw_0_total} MB")
    print(f"Maximum mem_bw_1_local: {max_mem_bw_1_local} MB")
    print(f"Maximum mem_bw_1_total: {max_mem_bw_1_total} MB")
    print(f"Total Average mem_bw_local: {(average_mem_bw_0_local + average_mem_bw_1_local):.2f} MB")
    print(f"Total Average mem_bw_total: {(average_mem_bw_0_total + average_mem_bw_1_total):.2f} MB")
    print(f"Total Maximum mem_bw_local: {(max_mem_bw_0_local + max_mem_bw_1_local):.2f} MB")
    print(f"Total Maximum mem_bw_total: {(max_mem_bw_0_total + max_mem_bw_1_total):.2f} MB")
    


def process_cpu_util(LOG_CPUUTIL):
    log_file_path = LOG_CPUUTIL
    pattern = r"\-\s*\-\s*\-"
    min_cpuutil = 10.00
    # Read and process the log file line by line
    cpu_utils=[]
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = re.search(pattern, line)
            if match:
                value = line.strip().split()[4]
                print(f"value={value}")
                cpu_utils.append(float(value))
    
    # rm unneed data
    new_cpu_utils = [value for value in cpu_utils if value >= min_cpuutil]
    median_value = statistics.median(new_cpu_utils)
    average_value = statistics.mean(new_cpu_utils)
    max_value = max(new_cpu_utils)
    print(f"LOG_CPUUTIL={LOG_CPUUTIL}")
    print(f"max_cpu:{max_value:.2f},avg_cpu:{average_value:.2f},med_cpu:{median_value:.2f}")
            


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", '-l',type=str, default="./process_metrics.log", help="log file name")
    parser.add_argument("--type", '-t',type=str, default="MEMBW", help="MEMBW|CPUUTIL")
    parser.add_argument("--membw_log", '-m',type=str, help="membw log file name")
    parser.add_argument("--metric_file", '-f',type=str, help="metric log file name")
    parser.add_argument('--dry_run', action='store_true', help='Run the script in dry-run mode.')
    args = parser.parse_args()
    logger = init_logger(args.log_file)
    logger.info(f'the arguments: {args}')

    LOG_MEMBW = args.membw_log

    # -- dry_run ...
    if args.dry_run:
        logger.info(f'dry-run======>')
        exit(0)

    logger.info(f"type:{args.type}")
    if args.type == "MEMBW":
        process_membw(LOG_MEMBW)
    elif args.type == "CPUUTIL":
        process_cpu_util(args.metric_file)
    
