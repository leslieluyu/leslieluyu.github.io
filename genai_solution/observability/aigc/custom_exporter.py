from prometheus_client import start_http_server, Gauge
import requests
import time
import json
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量获取配置
AIGC_UI_URL = os.getenv('AIGC_UI_URL', 'https://ai.idzcn.com/')
AIGC_ROUTER_URL = os.getenv('AIGC_ROUTER_URL', 'https://ai.idzcn.com/v1/chatqna')
AIGC_UI_INTERVAL = int(os.getenv('AIGC_UI_INTERVAL', 30))  # 默认 30 秒
AIGC_ROUTER_INTERVAL = int(os.getenv('AIGC_ROUTER_INTERVAL', 600))  # 默认 10 分钟

# 定义指标
AIGC_UI_RESPONSE_STATUS_CODE = Gauge(
    'aigc_ui_response_status_code',
    'AIGC UI HTTP 响应状态码',
    ['url']  # 标签用于区分不同 URL
)

AIGC_ROUTER_RESPONSE_STATUS_CODE = Gauge(
    'aigc_router_response_status_code',
    'AIGC Router HTTP 响应状态码',
    ['url']  # 标签用于区分不同 URL
)

def check_http_status(url, method='GET', headers=None, data=None):
    try:
        logging.info(f"Checking HTTP status for URL: {url} with method: {method}")
        if method == 'POST':
            response = requests.post(url, headers=headers, data=data, timeout=5)
        else:
            response = requests.get(url, timeout=5)
        status_code = response.status_code
        logging.info(f"Received status code {status_code} for URL: {url}")
    except Exception as e:
        status_code = 0  # 标记为失败
        logging.error(f"Error while checking HTTP status for URL: {url}. Error: {e}")
    return status_code

if __name__ == '__main__':
    # 启动指标服务器（端口 8000）
    logging.info("Starting Prometheus metrics server on port 8000")
    start_http_server(8000)

    # 每 AIGC_UI_INTERVAL 秒检测一次 AIGC UI
    def monitor_aigc_ui():
        while True:
            logging.info(f"Monitoring AIGC UI at {AIGC_UI_URL}...")
            status = check_http_status(AIGC_UI_URL)
            AIGC_UI_RESPONSE_STATUS_CODE.labels(url=AIGC_UI_URL).set(status)
            logging.info(f"AIGC UI status updated: {status}")
            time.sleep(AIGC_UI_INTERVAL)

    # 每 AIGC_ROUTER_INTERVAL 秒检测一次 AIGC Router
    def monitor_aigc_router():
        while True:
            logging.info(f"Monitoring AIGC Router at {AIGC_ROUTER_URL}...")
            headers = {"Content-Type": "application/json"}
            data = json.dumps({
                "messages": "What is the revenue of Nike in 2023?",
                "k": 10,
                "score_threshold": 0.5,
                "top_n": 1,
                "max_tokens": 1,
                "collection_name": "AIGC"
            })
            status = check_http_status(AIGC_ROUTER_URL, method='POST', headers=headers, data=data)
            AIGC_ROUTER_RESPONSE_STATUS_CODE.labels(url=AIGC_ROUTER_URL).set(status)
            logging.info(f"AIGC Router status updated: {status}")
            time.sleep(AIGC_ROUTER_INTERVAL)

    # 启动两个监控线程
    import threading
    logging.info("Starting monitoring threads for AIGC UI and Router")
    threading.Thread(target=monitor_aigc_ui, daemon=True).start()
    threading.Thread(target=monitor_aigc_router, daemon=True).start()

    # 保持主线程运行
    while True:
        time.sleep(1)
