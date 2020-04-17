import subprocess
import os
import time
import json
import re
import random as r
import concurrent.futures as cf

import boto3

ST_TI = time.perf_counter()
BASE_DIR = "https://project-vae.s3-us-west-2.amazonaws.com/"

MAX_COUNT = 5
MAX_WORKERS = 100

s3 = boto3.resource('s3')

bucket = s3.Bucket('project-vae')

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

    for date in dates:
        objects[date] = [
            img.key for img in bucket.objects.filter(Prefix=f'nclt/{date}')
        ]

    json.dump(objects, open('all_images.json', 'w'), indent=2)


def download_all(MAX_COUNT=MAX_COUNT, MAX_WORKERS=MAX_WORKERS):
    tasks = []
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


if __name__ == "__main__":
    download_s3_data()
    objects = json.load(open('all_images.json', 'r'))

    for obj in objects:
        print(len(objects[obj]))
    raise SystemExit

    download_all()

    print(time.perf_counter() - ST_TI)
