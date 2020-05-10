import subprocess
import os
import time
import json
import re
import random as r
import concurrent.futures as cf

import boto3

BASE_DIR = "https://project-vae.s3-us-west-2.amazonaws.com/"

MAX_COUNT = 5
MAX_WORKERS = 100

s3 = boto3.resource("s3")

bucket = s3.Bucket("project-vae")

dates = [
    "2012-01-08",
    "2012-01-15",
    "2012-03-17",
    "2012-04-29",  # Spring
    "2012-06-15",  # Summer
    "2012-08-04",
    "2012-09-28",  # Autumn
    "2012-10-28",
    "2012-11-04",
]


def download_s3_data():
    objects = {}

    with cf.ThreadPoolExecutor() as e:
        jobs = {}
        for date in dates:
            jobs[
                e.submit(
                    lambda x: [
                        img.key for img in bucket.objects.filter(Prefix=f"nclt/{x}")
                    ],
                    date,
                )
            ] = date

        for job in cf.as_completed(jobs):
            date = jobs[job]
            objects[date] = job.result()

    json.dump(objects, open("all_images.json", "w"), indent=2)


def download_all(objects, MAX_COUNT=MAX_COUNT, MAX_WORKERS=MAX_WORKERS):
    for obj in objects:
        try:
            down_obj = r.choices(objects[obj], k=MAX_COUNT)
            os.makedirs(obj, exist_ok=True)
            with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as e:
                e.map(
                    bucket.download_file,
                    down_obj,
                    [re.search(r"(?<=/).*", img).group(0) for img in down_obj],
                )

        except IndexError:
            pass


def update_and_show_data():
    st_ti = time.perf_counter()

    download_s3_data()
    objects = json.load(open("all_images.json", "r"))

    for date in dates:
        no_of_items = len(objects[date])
        if no_of_items == 0:
            break
        value = no_of_items
        print(no_of_items)

    print(time.perf_counter() - st_ti)
    return time.time(), value


def get_len_of_date(date):
    size = sum(1 for _ in bucket.objects.filter(Prefix=f"nclt/{date}"))
    print(f"{date=}, {size=}")
    return time.time(), size


def rolling_average(orig, n, d):
    new = n / d
    return (orig + new) / 2


if __name__ == "__main__":

    st_ti = time.perf_counter()

    imgs_per_sec = 0
    cycles = 1
    date = "2012-10-28"

    for _ in range(cycles):
        _1st_time, _1st_value = get_len_of_date(date)
        _2nd_time, _2nd_value = get_len_of_date(date)

        n = _2nd_value - _1st_value
        d = _2nd_time - _1st_time

        imgs_per_sec = rolling_average(imgs_per_sec, n, d)

        print(f"{_1st_time=}, {_1st_value=}")
        print(f"{_2nd_time=}, {_2nd_value=}\n===\n{imgs_per_sec=}")

    print(f"\nFinal {imgs_per_sec=}\nafter {cycles} cycle(s).")

    print(f"{(time.perf_counter() - st_ti)/60:3f} minutes")

    # download_all(objects)
