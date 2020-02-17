import tarfile
import zipfile
import numpy as np

NPY_FILES = [
    'summer2015_winter_gt_matchings.npy'
    ]


def extract_tar_file(tar_file='FAS_dataset.tar'):
    with tarfile.TarFile(tar_file) as f:
        # f.extractall()
        return f.getnames()


def view_zip_files(*zip_files):
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file) as z:
            print(zip_file, len(z.namelist()))


def open_npy_files(*npy_files):
    for npy_file in npy_files:
        matched_photos = np.load(npy_file)
        print(len(matched_photos))


if __name__ == "__main__":
    # view_zip_file(*extract_tar_file())
    open_npy_files(*NPY_FILES)
