import asyncio
import aiofiles
# import aiohttp
import re
import json
import os
import logging

from os import path as path
from google_images_download import google_images_download
# from pprint import pprint
from aiohttp import ClientSession
from pathlib import PurePath


# Setting path to project folder
os.chdir(path.dirname(path.realpath(__file__)))

# Setting logging file
logging.basicConfig(
    filename='dataset prep.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

SEARCH_CONFIG_PATH = "searchcfg.json"
MAIN_DATASET_URL_PATH = "dataset_urls.json"
JSON_FILES = ['summer trees.json', 'winter trees.json', 'autumn trees.json',
              'cherry blossom trees.json']
FOLDER_NAMES = ['dataset/summer trees/', 'dataset/winter trees/',
                'dataset/autumn trees/', 'dataset/cherry blossom trees/']


def url_download(argument_file):
    g = google_images_download.googleimagesdownload()

    paths = g.download({"config_file": argument_file})
    logging.debug(paths)

    json.dump(paths[0], open("dataset_urls.json", "w"), indent=2)


async def zenserp_search(q, session, offset=0, folder_name=None):

    if folder_name is None:
        folder_name = q

    os.makedirs(f"dataset/{folder_name}", exist_ok=True)

    headers = {"apikey": os.getenv("ZENSERP_KEY")}

    params = (
        ("q", folder_name),
        ("device", "desktop"),
        ("tbm", "isch"),
        ("start", "")
        ("tbs", "itp:photo,isz:l")
    )
    async with session.get(
        url="https://app.zenserp.com/api/v2/search",
        headers=headers,
        params=params
    ) as response:

        results = await response.json()

    json_file_name = f"{q}.json"
    json.dump(results, open(json_file_name, 'w'), indent=2)

    JSON_FILES.append(json_file_name)


def create_dataset_folders(folder_names):
    for folder_name in folder_names:
        os.makedirs(folder_name, exist_ok=True)


async def download_image(image_obj, session, folder_name='', file_name=None,
                         chunk_size=100, sem=None):

    async with sem:
        logging.debug(image_obj)
        image_url = image_obj["sourceUrl"]

        try:
            async with session.get(image_url, verify_ssl=False) as resp:
                file_suffix = PurePath(image_url).suffix or ".jpg"
                file_suffix = re.sub(r"[?&!].*", "", file_suffix)
                file_suffix = file_suffix if file_suffix.isalpha()\
                    else ".jpg"

                file_name = f"{folder_name}{file_name or image_obj['position']}\
{file_suffix}"

                async with aiofiles.open(
                    file_name,
                    "wb"
                ) as f:

                    while True:
                        chunk = await resp.content.read(chunk_size)
                        if not chunk:
                            break
                        await f.write(chunk)
        except Exception as e:
            logging.error(image_url, e)
        logging.info(f"Downloaded {image_obj['position']}: {image_url}")


async def download_images_from_json(json_files, folder_names):
    assert len(json_files) == len(folder_names)

    sem = asyncio.Semaphore(50)
    async with ClientSession() as session:
        tasks = [
            download_image(
                image_obj,
                session,
                folder_name=folder_names[index],
                sem=sem
            )

            for index in range(len(json_files))
            for image_obj in
            json.load(open(json_files[index], 'r'))
        ]

        await asyncio.gather(*tasks)


def parse_dataset_urls(json_file_name):
    dataset_img_link_dict = json.load(open(json_file_name))
    for key in dataset_img_link_dict:
        value = [
            {"position": index,
             "sourceUrl": dataset_img_link_dict[key][index]}
            for index in range(len(dataset_img_link_dict[key]))
        ]

        json.dump(value, open(key+".json", 'w'), indent=2)
        print(f"Saved {key} in {key}.json!")


if __name__ == "__main__":
    # parse_dataset_urls(MAIN_DATASET_URL_PATH)
    create_dataset_folders(FOLDER_NAMES)
    asyncio.run(download_images_from_json(
        JSON_FILES,
        FOLDER_NAMES
    ))

    # url_download(SEARCH_CONFIG_PATH)
