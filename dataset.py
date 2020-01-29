import asyncio
import aiofiles
import aiohttp
import json
import re
import os

from google_images_download import google_images_download
from pprint import pprint
from aiohttp import ClientSession
from pathlib import PurePath

SEARCH_CONFIG_PATH = "searchcfg.json"
JSON_FILES = ['summer trees.json', 'winter trees.json']
FOLDER_NAMES = ['dataset/summer trees/', 'dataset/winter trees/']


def url_download(argument_file):
    g = google_images_download.googleimagesdownload()
    args = json.load(open(argument_file))

    paths = g.download(args)
    print(paths)

    json.dump(open("dataset_urls.json", "w"), indent=2)


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
        pprint(image_obj)
        image_url = image_obj["sourceUrl"]

        try:
            async with session.get(image_url, verify_ssl=False) as resp:
                file_suffix = PurePath(image_url).suffix or ".jpg"
                file_suffix = re.sub(r"[?&].*", "", file_suffix)

                async with aiofiles.open(
                    f"{folder_name}{file_name or image_obj['position']}{file_suffix}",
                    "wb"
                ) as f:

                    while True:
                        chunk = await resp.content.read(chunk_size)
                        if not chunk:
                            break
                        await f.write(chunk)
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print(image_url, e)
        print(f"Downloaded {image_obj['position']}: {image_url}")


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
            json.load(open(json_files[index], 'r'))['image_results'][:10]
        ]

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # create_dataset_folders(FOLDER_NAMES)
    # asyncio.run(download_images_from_json(
    #     JSON_FILES,
    #     FOLDER_NAMES
    # ))

    url_download(SEARCH_CONFIG_PATH)
