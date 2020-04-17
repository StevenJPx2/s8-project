import os
import subprocess
import concurrent.futures as cf


def travel_dir(dir_name, date, count=0, cmd_list=None):
    if cmd_list is None:
        cmd_list = []
    for path in os.listdir(dir_name):
        full_path = os.path.join(dir_name, path)
        print(full_path)
        if not os.path.isdir(full_path):
            s3_path = f"s3://project-vae/nclt/\
{date}/{full_path.split('/')[-1]}"

            cmd = ["aws", "s3", "cp", full_path, s3_path]

            if count < 21000:
                cmd_list.append(cmd)
            else:
                return cmd_list
            count += 1
        else:
            travel_dir(full_path, date, count, cmd_list)

    return cmd_list


date = "hello"

cmd_list = travel_dir(os.path.abspath('hello'), date)
print(cmd_list)
with cf.ThreadPoolExecutor(max_workers=100) as e:
    e.map(lambda x: subprocess.call(x, shell=True), cmd_list)
