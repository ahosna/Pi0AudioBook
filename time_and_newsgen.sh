#!/bin/bash

NEWS_FILE="/data/.news.mp3"
ANNOUNCER_FILE="/data/tmp/.anziko.mp3"

if [ ! -f $NEWS_FILE ]; then
    exit 0
fi

tf=`date +times/%0Hh-%0Mm.mp3`
ffmpeg -i "concat:$tf|$NEWS_FILE" -c copy $ANNOUNCER_FILE
exit 0
