import multiprocessing
import time


def increment(count):
    while True:
        time.sleep(1)
        count.value += 1


if __name__ == "__main__":
    count = multiprocessing.Value("i", 0)
    process = multiprocessing.Process(target=increment, args=(count,))
    process.start()
    while True:
        time.sleep(5)
        print(count.value)
