import os
import subprocess
import tarfile
import logging

logging.basicConfig(
    filename="dataset prep.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# DOWNLOAD IMAGES

base_dir = "http://robots.engin.umich.edu/nclt"

dates = [
    '2012-01-08',
    "2012-01-15",
    "2012-01-22",
    "2012-02-02",
    "2012-02-04",
    "2012-02-05",
    "2012-02-12",
    "2012-02-18",
    "2012-02-19",
    "2012-03-17",
    "2012-03-25",
    "2012-03-31",
    "2012-04-29",
    "2012-05-11",
    "2012-05-26",
    "2012-06-15",
    "2012-08-04",
    "2012-08-20",
    "2012-09-28",
    "2012-10-28",
    "2012-11-04",
    "2012-11-16",
    "2012-11-17",
    "2012-12-01",
    "2013-01-10",
    "2013-02-23",
    "2013-04-05",
]

dates = [
    "2012-06-15",  # Summer
    "2012-08-04",
    "2012-09-28",  # Autumn
    "2012-10-28",
    "2012-11-04",
]


def travel_dir(dir_name, date, count=0, cmd_list=None):
    if cmd_list is None:
        cmd_list = []
    for path in os.listdir(dir_name):
        full_path = os.path.join(dir_name, path)
        if not os.path.isdir(full_path):
            s3_path = f"s3://project-vae/nclt/\
{date}/{full_path.split('/')[-1]}"

            cmd = ["aws", "s3", "cp", full_path, s3_path]
            cmd = " ".join(cmd)

            logging.debug(f"Uploading {full_path} \
-> {s3_path}")
            if count < 21000:
                cmd_list.append(cmd)
            else:
                return cmd_list
            count += 1
            logging.debug(f"Uploaded {full_path} \
-> {s3_path}")
        else:
            travel_dir(full_path, date, count, cmd_list)

    return cmd_list


os.makedirs("images", exist_ok=True)
try:
    for date in dates:
        cmd = [
            "wget",
            "--continue",
            f"{base_dir}/images/{date}_lb3.tar.gz",
            "-P",
            "images",
        ]
        logging.info("Calling: " + " ".join(cmd))
        subprocess.call(cmd)

        # OPENING ZIPPED FILE
        archive_path = f"images/{date}_lb3.tar.gz"
        folder_path = archive_path.replace(".tar.gz", "/")

        with tarfile.open(archive_path, "r:gz") as f:
            logging.info(f"Extracting {archive_path} -> {folder_path}")
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(f, folder_path)

        logging.info(f"Extracted {archive_path} -> {folder_path}")
        ######################

        # REMOVING ZIPPED FILE AFTER EXTRACTION
        subprocess.call(["rm", archive_path])
        logging.info(f"Removed {archive_path}")
        #####################

        # UPLOADING TO S3
        cmd_list = travel_dir(os.path.abspath(folder_path), date)
        for cmd in cmd_list:
            os.system(cmd)
        logging.info(f"Uploaded all {folder_path} images")
        ##################

        # REMOVING UNZIPPED FOLDER
        subprocess.call("rm -r " + folder_path, shell=True)
        logging.info(f"Removed {folder_path} directory")
        ##########################

except Exception as e:
    logging.error(e)
