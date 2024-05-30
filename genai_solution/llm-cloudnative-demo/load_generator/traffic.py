import concurrent.futures
import requests
import time
import random

# Define the URL and payload data for the POST requests
url = "http://llm.intel.com/v2/completions" # ingress
#url = "http://172.16.28.130:8000/v2/completions"  # docker in r028s013

#url = "http://llm.intel.com/v1/completions"
#url = "http://172.16.28.100:30021/v1/completions"
payload = {
    "prompt": "What is AI?",
    "max_length":32,
    "history": []
}
headers = {
    "Content-Type": "application/json"
}
request_times = {}        

# 请求发送函数
def send_request(url, request_num):
    ram = random.randint(2, 3)
    print(f"Request {request_num}: Wait for  random {ram} seconds")
    time.sleep(ram)
    try:
        start_time = time.time()
        request_times[request_num] = start_time
        print(f"Request {request_num} started ...")
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        duration = time.time() - request_times.pop(request_num)
        print(f"Request {request_num} took {duration:.2f} seconds")
        print(f"Request {request_num} - Status:", response_data["status"])
        print("Total Duration:", response_data.get("total_dur", "N/A"))
        print("Prompt Tokens:", response_data.get("prompt_tokens", "N/A"))
        print("Completion Tokens:", response_data.get("completion_tokens", "N/A"))
        print("Latency per Token:", response_data.get("latency_per_token", "N/A"))
        print("\n")
        print(f"Request {request_num}: Response from {url} , ramdom {ram}") #: {response.status_code}")
        return response_data

    except requests.RequestException as e:
         return f"Error sending request to {url}: {e}"

    

# 主函数
def main():
    # 要发送的请求的URL
    #url = "https://www.example.com"
    
    request_counter = 0  # 自增编号计数器
    max_workers = 20  # 最大线程数

    # 创建线程池，最多同时执行3个线程
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = set()
        while True:
            print(f"Current Max Workers of executor is  {executor._max_workers} workers...")
            # 使用 for 循环确保初始时并发3个请求
            for _ in range(max_workers  - len(futures)):
                
                print(f"Will submit {max_workers  - len(futures)} workers...")
                request_counter += 1  # 自增编号

                # 提交任务给线程池，实现并发发送请求，传入自增编号
                future = executor.submit(send_request, url, request_counter)
                futures.add(future)

            # 使用 wait 等待任何一个请求完成
            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
            
            # 遍历完成的future
            failed_count = 0
            for future in done:
                print(" a future in done")
                response_data = future.result()
                print(response_data)
                if "502 Server Error: Bad Gateway" in str(response_data):
#                if response_data == "ERROR":
                    print("Request failed")
                    failed_count = failed_count +1
                else:
                    # 正常处理结果
                    print("Request succeeded")
            

            # 移除已完成的请求
            futures.difference_update(done)
            
            # adjust the new size of threadpool
            if failed_count > 0:
                print(f"There are {failed_count} failed request out of {max_workers} max requests!!!")
                max_workers =  max_workers - failed_count
                print(f"Let's adjusted the max thread count to new size {max_workers}")
                executor._max_workers = max_workers
                print(f"Finished adjusted the max thread count to new size {max_workers}")
            print("---\n---\n")

if __name__ == "__main__":
    main()
