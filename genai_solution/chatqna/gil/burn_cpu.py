import threading


def burn_cpu():
    while True:
        pass


def main():

    num_threads = 4
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=burn_cpu)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":

    main()