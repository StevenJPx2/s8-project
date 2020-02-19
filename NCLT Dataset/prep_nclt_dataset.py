import os
import subprocess
import tarfile

# DOWNLOAD IMAGES

base_dir = 'http://robots.engin.umich.edu/nclt'

dates = [
    '2012-01-08',
    '2012-01-15',
    '2012-01-22',
    '2012-02-02',
    '2012-02-04',
    '2012-02-05',
    '2012-02-12',
    '2012-02-18',
    '2012-02-19',
    '2012-03-17',
    '2012-03-25',
    '2012-03-31',
    '2012-04-29',
    '2012-05-11',
    '2012-05-26',
    '2012-06-15',
    '2012-08-04',
    '2012-08-20',
    '2012-09-28',
    '2012-10-28',
    '2012-11-04',
    '2012-11-16',
    '2012-11-17',
    '2012-12-01',
    '2013-01-10',
    '2013-02-23',
    '2013-04-05'
]

os.makedirs('images', exist_ok=True)
for date in dates:
    cmd = ['wget', '--continue',
           '%s/images/%s_lb3.tar.gz' % (base_dir, date),
           '-P', 'images']
    print("Calling: ", ' '.join(cmd))
    subprocess.call(cmd)

    # OPENING ZIPPED FILE
    archive_path = f"images/{date}_lb3.tar.gz"

    with tarfile.TarFile(archive_path) as f:
        folder_path = archive_path.split('.')[0]
        f.extractall(folder_path)

    subprocess.call(['rm', archive_path])

    # UPLOADING TO S3
    subprocess.call([
        'aws s3 cp',
        folder_path,
        f"s3://project-vae/nclt/{folder_path}"
        ])
    subprocess.call(['rm -r', folder_path])
