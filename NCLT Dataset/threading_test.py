import concurrent.futures as cf
import time


def thread_fn(name=''):
    print(f'Starting worker: {name}')
    time.sleep(2)


if __name__ == "__main__":
    with cf.ThreadPoolExecutor(max_workers=4) as e:
        e.map(thread_fn, range(10))
