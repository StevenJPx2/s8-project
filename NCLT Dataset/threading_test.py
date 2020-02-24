import concurrent.futures as cf
import time
import wget
import os
import subprocess

store_dir_name = "lol"

full_path = os.path.join(os.getcwd(), store_dir_name+"/")

links = [
    "www.google.com",
    "www.apple.com",
    "www.youtube.com",
    "support.google.com",
    "play.google.com",
    "www.blogger.com",
    "www.microsoft.com",
    "docs.google.com",
    "accounts.google.com",
    "www.mozilla.org"
]

links = list(map(lambda x: "https://"+x, links))


def thread_fn(name='', fn=None, *args, **kwargs):
    print(f'Starting worker: {name}')
    if fn is None:
        time.sleep(2)
    else:
        print(f"{fn}{args}{kwargs}")
        fn(*args, **kwargs)
    print(f'\nExiting worker: {name}')


if __name__ == "__main__":
    os.makedirs(full_path, exist_ok=True)
    os.chdir(full_path)
    timer_start = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=4) as e:
        e.map(
            thread_fn,
            range(10),
            [wget.download]*10,
            links
            )
    timer_diff = time.perf_counter() - timer_start
    print(timer_diff)
    subprocess.call("rm -rf *", shell=True)

    print("\n\n............\nSynchronous\n............\n\n")
    timer_start = time.perf_counter()
    for counter in range(10):
        thread_fn(counter, wget.download, links[counter])

    timer_diff = time.perf_counter() - timer_start
    print(timer_diff)
    subprocess.call("rm -rf *", shell=True)
