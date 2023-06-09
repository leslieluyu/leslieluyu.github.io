import time
def foo(n):
    result = 0
    for _ in range(n):
        result += 1
    return result

def bar(n):
    foo(n)

def baz(n):
    bar(n)

if __name__ == "__main__":
    print("begin of baz 10000000")
    start_time = time.monotonic_ns()  # get the start time in nanoseconds
    baz(1000000)
    end_time = time.monotonic_ns()  # get the end time in nanoseconds
    execution_time = (end_time - start_time) / 1000000  # convert to milliseconds
    print("end of  baz 10000000")
    print("Execution time:", execution_time, "milliseconds")