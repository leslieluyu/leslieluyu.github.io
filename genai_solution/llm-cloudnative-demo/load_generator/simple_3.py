import requests
from concurrent.futures import ThreadPoolExecutor

def send_request(url, data):
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("请求成功！")
        print("响应内容：")
        print(response.json())
    else:
        print(f"请求失败，状态码：{response.status_code}")

def main():
    url = "http://llm.intel.com/v1/completions"
    data = {
        "prompt": "What is AI?",
        "history": []
    }
    
    num_requests = 5

    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        for _ in range(num_requests):
            executor.submit(send_request, url, data)

if __name__ == "__main__":
    main()