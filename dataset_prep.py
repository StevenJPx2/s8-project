import asyncio
import json
import os
import re
from pathlib import PurePath
from pprint import pprint

import aiofiles
from aiohttp import ClientSession


async def google_search_and_download(q, session, offset=0, folder_name=None):

    if folder_name is None:
        folder_name = q

    os.makedirs(f"dataset/{folder_name}", exist_ok=True)

    headers = {"apikey": "86c55520-03bc-11ea-babc-6de1d7050177"}

    params = (
        ("q", folder_name),
        ("device", "desktop"),
        ("tbm", "isch"),
        ("tbs", "itp:photo,isz:l")
    )

    response = await session.request(
        method="GET",
        url="https://app.zenserp.com/api/v2/search",
        headers=headers,
        params=params
    )

    results = await response.json()
    json.dump(results, open(f"{q}.json", 'w'))

    await download_images(results, session)


async def download_images(results, session, is_file=False):

    if is_file:
        results = json.load(open(results, 'r'))

    for image_obj in results["image_results"]:
        image_url = image_obj["sourceUrl"]
        pprint(image_obj)

        file_suffix = PurePath(image_url).suffix
        re.sub(r"\?.*", "", file_suffix)

        async with aiofiles.open(
            f"{image_obj['position']}{file_suffix}",
            "wb"
        ) as f:
            image = await session.request(
                method="GET",
                url=image_url
            )

            image.raise_for_status()

            if is_file:
                try:
                    os.chdir(f"dataset/{is_file}")
                except FileNotFoundError:
                    os.chdir("../..")

            while True:
                try:
                    await f.write(await image.read())
                except EOFError:
                    pass


async def bulk_download(queries, from_file=False):

    async with ClientSession() as session:
        if from_file is False:
            tasks = [google_search_and_download(q, session) for q in queries]
        else:
            assert len(queries) == len(from_file)
            tasks = [download_images(queries[index],
                                     session,
                                     from_file[index])
                     for index in range(len(queries))]
        pprint(tasks)
        await asyncio.gather(*tasks)

if __name__ == "__main__":

    # asyncio.run(bulk_download(["summer trees", "winter trees"]))
    asyncio.run(bulk_download(
        ["summer trees.json", "winter trees.json"],
        ["summer trees", "winter trees"]
    ))
