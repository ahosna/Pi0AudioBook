#!/bin/bash

NEWS_FILE="/data/tmp/.news.mp3"
ANNOUNCER_FILE_TMP="/data/tmp/.tmpanziko.mp3"
ANNOUNCER_FILE="/data/tmp/.anziko.mp3"

tf=`date +/home/pi/Pi0AudioBook/times/%0Hh-%0Mm.mp3`
if [ ! -f $NEWS_FILE ]; then
    cp $tf $ANNOUNCER_FILE_TMP
else
    ffmpeg -y -i "concat:$tf|$NEWS_FILE" -c copy $ANNOUNCER_FILE_TMP
fi
mv -f $ANNOUNCER_FILE_TMP $ANNOUNCER_FILE
exit 0
