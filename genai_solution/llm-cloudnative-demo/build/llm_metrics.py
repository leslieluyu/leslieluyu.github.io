from prometheus_client import start_http_server, CollectorRegistry, Gauge

registry = CollectorRegistry()
# Define metric names and descriptions
metrics = {
    'request_total_dur_s': 'total duration in seconds',
    'request_prompt_tokens': 'prompt tokens num',
    'request_completion_tokens': "complete tokens num",
    'request_total_token_latency_s': 'total latency of tokens in seconds',
    'request_first_token_latency_ms': 'latency of first token in ms',
    'request_next_token_latency_ms': 'latency of next tokens in ms',
    'request_avg_token_latency_ms': 'average latency of tokens in ms',
    'request_status': 'Request Status Code'
}

# Create a dictionary to store Gauge instances
request_gauge = {}

# Create Gauge instances and store them in the dictionary
for metric_name, description in metrics.items():
    request_gauge[metric_name] = Gauge(metric_name, description, registry=registry)

class RequestMetrics:
  def __init__(self, total_dur,prompt_tokens,completion_tokens,latency_per_token, status):
    self.total_dur = total_dur
    self.prompt_tokens = prompt_tokens
    self.completion_tokens = completion_tokens
    self.latency_per_token = latency_per_token
    self.status = status

  def __init__(self, metrics_dic):
    self.metrics_dic = metrics_dic
    for key, value in metrics_dic.items():
      print(key, value)




def process_request_metrics(request_metrics):
    for metric_name, description in metrics.items():
      key = metric_name.replace("request_", "")
      value = request_metrics.metrics_dic[key]
      print(f"metric_name={metric_name},key={key},value={value}")
      request_gauge[metric_name].set(value)

  # request_total_dur.set(request_metrics.total_dur)
  # request_prompt_tokens.set(request_metrics.prompt_tokens)
  # request_completion_tokens.set(request_metrics.completion_tokens)
  # request_latency_per_token.set(request_metrics.latency_per_token)
  # request_status.set(request_metrics.status)


def start_metrics_server(metric_port):
  print(f"start_http_server,metric_port:{metric_port}")
  start_http_server(metric_port, registry=registry)



