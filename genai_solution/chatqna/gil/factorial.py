import math
import queue
import threading
import time


def compute_partial_factorial(start, end):

    partial_factorial = 1
    for i in range(start, end):
        partial_factorial *= i
    return partial_factorial


def compute_factorial_multithread(num, num_threads):

    threads = []
    results = queue.Queue()
    chunk_size = num // num_threads
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = num + 1 if i == num_threads - 1 else (i + 1) * chunk_size + 1
        thread = threading.Thread(
            target=lambda s, e: results.put(compute_partial_factorial(s, e)),
            args=(start, end))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    total_factorial = 1
    while not results.empty():
        total_factorial *= results.get()
    return total_factorial


def main():

    num_repeats = 20
    num = 100000
    factorial_ground_truth = math.factorial(num)
    num_threads = 4
    factorial_multithread = compute_factorial_multithread(num, num_threads)
    assert factorial_ground_truth == factorial_multithread
    # Time the factorial computation
    start_time = time.time()
    for _ in range(num_repeats):
        factorial_multithread = compute_factorial_multithread(num, num_threads)
    end_time = time.time()
    print(
        f"Average Time Elapsed: {(end_time - start_time) / num_repeats:.2f}s")


if __name__ == "__main__":

    main()