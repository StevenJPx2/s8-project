import subprocess
import os
import time
import boto3
import json
import random as r

st_ti = time.perf_counter()

MAX_COUNT = 5

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
        objects[date] = [img.key for img in bucket.objects.filter(Prefix=f'nclt/{date}')]
    
    json.dump(objects, open('all_images.json', 'w'), indent=2)



download_s3_data()

objects = json.load(open('all_images.json', 'r'))

for obj in objects:
    print(len(objects[obj]))

raise SystemExit


for obj in objects:
    try:
        down_obj = r.choices(objects[obj], k=MAX_COUNT)
        os.makedirs(obj, exist_ok=True)
        for dow in down_obj:
            bucket.download_file(dow, "/".join(dow.split("/")[-2:]))
        
    except IndexError:
        pass

print(time.perf_counter() - st_ti)


