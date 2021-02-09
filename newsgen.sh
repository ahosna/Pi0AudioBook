#!/bin/bash

MY_PATH=/home/pi/knihaui
. $MY_PATH/env/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$MY_PATH/env/newsgen-credentials.json"
cd $MY_PATH
python3 ./newsgen.py
exit $?
