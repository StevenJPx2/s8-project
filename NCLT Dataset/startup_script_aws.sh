curl -o prep.py https://raw.githubusercontent.com/StevenJPx2/s8-project/master/NCLT%20Dataset/prep_nclt_dataset.py;
screen -dmS preppy;
screen -S preppy -p 0 -X stuff $'python3 prep.py\n';
