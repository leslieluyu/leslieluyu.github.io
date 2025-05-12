import queue
import threading
import time


def compute_sum(arr, start, end):

    sum = 0
    for i in range(start, end):
        sum += arr[i]
    return sum


def compute_sum_multithread(arr, num_threads):

    n = len(arr)
    chunk_size = n // num_threads
    threads = []
    results = queue.Queue()
    for i in range(num_threads):
        start = i * chunk_size
        end = n if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(
            target=lambda s, e: results.put(compute_sum(arr, s, e)),
            args=(start, end))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    sum = 0
    while not results.empty():
        sum += results.get()
    return sum


def main():

    num_repeats = 20
    num_elements = 10000000
    arr = list(range(1, num_elements + 1))
    sum_ground_truth = num_elements * (num_elements + 1) // 2
    num_threads = 4
    sum_multithread = compute_sum_multithread(arr, num_threads)
    assert sum_ground_truth == sum_multithread
    # Time the sum computation
    start_time = time.time()
    for _ in range(num_repeats):
        sum_multithread = compute_sum_multithread(arr, num_threads)
    end_time = time.time()
    print(
        f"Average Time Elapsed: {(end_time - start_time) / num_repeats:.2f}s")


if __name__ == "__main__":

    main()