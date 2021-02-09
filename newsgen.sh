#!/bin/bash

MY_PATH=/home/adino/code/Pi0AudioBook
. $MY_PATH/env/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$MY_PATH/env/newsgen-credentials.json"
cd $MY_PATH
python3.7 ./newsgen.py

scp /tmp/.news.mp3 kniha:/data/.news.mp3

exit $?
