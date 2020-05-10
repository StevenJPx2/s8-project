import os
import logging
import asyncio
import shlex

folder_path = "images/2012-08-04_lb3"
date = "2012-08-04"


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()


async def travel_dir(dir_name, date, count=0, cmd_list=None):
    if cmd_list is None:
        cmd_list = []
    for path in os.listdir(dir_name):
        full_path = os.path.join(dir_name, path)
        if not os.path.isdir(full_path):
            s3_path = f"s3://project-vae/nclt/{date}/{full_path.split('/')[-1]}"

            cmd = ["aws", "s3", "cp", full_path, s3_path]
            cmd = f"aws s3 cp '{full_path}' '{s3_path}'"

            logging.debug(f"Uploading {full_path} -> {s3_path}")
            if count < 21000:
                cmd_list.append(run(cmd))
            else:
                return cmd_list
            count += 1
            logging.debug(f"Uploaded {full_path} -> {s3_path}")
        else:
            travel_dir(full_path, date, count, cmd_list)

    await asyncio.gather(*cmd_list)


asyncio.run(travel_dir(os.path.abspath(folder_path), date))
