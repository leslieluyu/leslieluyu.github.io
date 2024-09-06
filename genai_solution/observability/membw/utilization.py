import re
import time
import requests
import logging
from prometheus_client.parser import text_string_to_metric_families
from collections import defaultdict
from threading import Thread, Event

# Configure logging
log_level = 'ERROR'  # Default log level
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

class MetricFetcher:
    def __init__(self, url: str):
        self.url = url
        self.metrics = defaultdict(list)
        self.stop_event = Event()
        self.thread = None

    def fetch_metrics(self, metric_names: list[str], namespace: str):
        """
        Fetches metrics from the specified URL, filters by metric name and namespace, and stores them in the class.
        """
        start_time = time.time()  # Start timer for fetching metrics
        response = requests.get(self.url)
        response.raise_for_status()
        metrics_data = response.text
        fetch_duration = time.time() - start_time  # Calculate duration

        logger.debug(f"Time taken to fetch metrics: {fetch_duration:.2f} seconds")

        start_time = time.time()  # Start timer for parsing metrics
        for family in text_string_to_metric_families(metrics_data):
            for sample in family.samples:
                metric_name = sample[0]
                labels = sample[1]
                value = sample[2]

                # Check if the metric name and namespace match
                if metric_name in metric_names and labels.get("nameSpace") == namespace:
                    container_id = labels.get("containerId")
                    container_name = labels.get("containerName")
                    self.metrics[container_id].append((metric_name, container_name, value))
        parse_duration = time.time() - start_time  # Calculate duration

        logger.debug(f"Time taken to parse metrics: {parse_duration:.2f} seconds")

    def calculate_average_and_max_per_container(self) -> dict[str, dict[str, any]]:
        result = {}
        start_time = time.time()  # Start timer for calculations
        for container_id, values in self.metrics.items():
            result[container_id] = {
                "container_name": values[0][1],  # Get the container name from the first entry
                "rdt_container_cpu_utilization": {
                    "values": [value for name, _, value in values if name == "rdt_container_cpu_utilization"],
                    "average": 0,
                    "max": 0
                },
                "rdt_container_local_memory_bandwidth": {
                    "values": [value for name, _, value in values if name == "rdt_container_local_memory_bandwidth"],
                    "average": 0,
                    "max": 0
                }
            }

            # Calculate average and max for each metric
            for metric_name in ["rdt_container_cpu_utilization", "rdt_container_local_memory_bandwidth"]:
                metric_values = result[container_id][metric_name]["values"]
                if metric_values:
                    result[container_id][metric_name]["average"] = sum(metric_values) / len(metric_values)
                    result[container_id][metric_name]["max"] = max(metric_values)

        calculation_duration = time.time() - start_time  # Calculate duration
        logger.debug(f"Time taken to calculate averages and max values: {calculation_duration:.2f} seconds")

        return result

    def fetch_metrics_periodically(self, metric_names: list[str], namespace: str, interval: int):
        while not self.stop_event.is_set():
            self.fetch_metrics(metric_names, namespace)
            self.stop_event.wait(interval)

    def start(self, metric_names: list[str], namespace: str, interval: int = 5):
        """
        Starts the periodic fetching of metrics.
        """
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self.fetch_metrics_periodically, args=(metric_names, namespace, interval))
            self.thread.start()
            logger.info("MetricFetcher started.")

    def stop(self):
        """
        Stops the periodic fetching of metrics.
        """
        if self.thread is not None and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
            self.stop_event.clear()
            logger.info("MetricFetcher stopped.")

    def save_results_to_file(self, stats: dict[str, dict[str, any]], file_path: str):
        """
        Saves the calculated statistics to a file.
        """
        with open(file_path, "w") as file:
            for container_id, container_stats in stats.items():
                file.write(f"Container ID: {container_id}\n")
                file.write(f"Container Name: {container_stats['container_name']}\n")
                file.write("rdt_container_cpu_utilization:\n")
                file.write(f"  Average: {container_stats['rdt_container_cpu_utilization']['average']}\n")
                file.write(f"  Max: {container_stats['rdt_container_cpu_utilization']['max']}\n")
                file.write("rdt_container_local_memory_bandwidth:\n")
                file.write(f"  Average: {container_stats['rdt_container_local_memory_bandwidth']['average']}\n")
                file.write(f"  Max: {container_stats['rdt_container_local_memory_bandwidth']['max']}\n")
                file.write("\n")

        logger.info(f"Results saved to: {file_path}")

# Example usage
if __name__ == "__main__":
    # Define the endpoint URL and result file path
    metrics_endpoint = "http://192.168.180.115:9100/metrics"  # Replace with your endpoint
    result_file_path = "result.txt"  # Replace with your desired result file path

    fetcher = MetricFetcher(metrics_endpoint)

    # Start the MetricFetcher
    fetcher.start(
        metric_names=["rdt_container_cpu_utilization", "rdt_container_local_memory_bandwidth"],
        namespace="benchmarking"
    )

    # Wait for some time
    time.sleep(15)

    # Stop the MetricFetcher
    fetcher.stop()

    # Calculate and print average and max per container
    stats = fetcher.calculate_average_and_max_per_container()

    # Save results to a file
    fetcher.save_results_to_file(stats, result_file_path)