#!/bin/bash

MY_PATH=/home/pi/Pi0AudioBook
. $MY_PATH/env/bin/activate
cd $MY_PATH
python3 ./knihaui.py
exit $?
