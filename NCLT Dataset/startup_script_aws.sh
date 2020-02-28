#!/bin/bash

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install



curl -o prep.py https://raw.githubusercontent.com/StevenJPx2/s8-project/master/NCLT%20Dataset/prep_nclt_dataset.py;
screen -dmS preppy;
screen -S preppy -p 0 -X stuff $'python3 prep.py\n';