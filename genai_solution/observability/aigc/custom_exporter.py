from prometheus_client import start_http_server, Gauge
import requests
import time

# 定义指标
HTTP_STATUS_CODE = Gauge(
    'http_response_status_code',
    'HTTP 响应状态码',
    ['url']  # 标签用于区分不同 URL
)

def check_http_status(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
    except Exception as e:
        status_code = 0  # 标记为失败
    return status_code

if __name__ == '__main__':
    # 启动指标服务器（端口 8000）
    start_http_server(8000)
    # 每 30 秒检测一次
    while True:
        status = check_http_status('https://ai.idzcn.com/')
        HTTP_STATUS_CODE.labels(url='ai.idzcn.com').set(status)
        time.sleep(30)
