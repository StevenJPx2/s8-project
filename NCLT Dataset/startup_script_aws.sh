#!/bin/bash

sudo apt-get install unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
export AWS_ACCESS_KEY_ID=AKIATS5JZNGO6ZB57DIE
export AWS_SECRET_ACCESS_KEY=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

curl -o prep.py https://raw.githubusercontent.com/StevenJPx2/s8-project/master/NCLT%20Dataset/prep_nclt_dataset.py;
screen -dmS preppy;
screen -S preppy -p 0 -X stuff $'python3 prep.py\n';