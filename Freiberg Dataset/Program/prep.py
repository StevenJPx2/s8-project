import os
from pathlib import Path

PARENT_PATH = Path("../Main FAS/").resolve()

# PREPARING SUMMER DATASET
for folder in ["camera0", "summer_icra_dataset"]:
    full_path = os.path.join(PARENT_PATH, folder)
    for image in os.listdir(full_path):
        os.system(f"mv '{full_path}/{image}' '{PARENT_PATH}/summer/'")


# PREPARING WINTER DATASET
for folder in ["winter_icra_dataset"]:
    full_path = os.path.join(PARENT_PATH, folder)
    for image in os.listdir(full_path):
        print(f"mv '{full_path}/{image}' '{PARENT_PATH}/winter/'")
        os.system(f"mv '{full_path}/{image}' '{PARENT_PATH}/winter/'")
