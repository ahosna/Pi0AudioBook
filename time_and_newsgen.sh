#!/bin/bash

NEWS_FILE="/data/tmp/.news.mp3"
STARTUP_FILE="/home/pi/Pi0AudioBook/msgs/startup.mp3"

ZURNAL_FILE="/data/tmp/.zurnal.mp3"
ZURNAL_NOT_READY="/home/pi/Pi0AudioBook/msgs/zurnal_not_ready.mp3"

ANNOUNCER_FILE_TMP="/data/tmp/.tmpanziko.mp3"
ANNOUNCER_FILE="/data/tmp/.anziko.mp3"

if [ ! -f $NEWS_FILE ]; then
    cp $STARTUP_FILE $ANNOUNCER_FILE_TMP
else
    tf=`date +/home/pi/Pi0AudioBook/times/%0Hh-%0Mm.mp3`
    ffmpeg -y -i "concat:$tf|$NEWS_FILE" -c copy $ANNOUNCER_FILE_TMP
fi
mv -f $ANNOUNCER_FILE_TMP $ANNOUNCER_FILE


# Create announcement that Zurnal is not ready yet
if [ ! -f $ZURNAL_FILE ]; then
    cp $ZURNAL_NOT_READY $ZURNAL_FILE
fi
exit 0
