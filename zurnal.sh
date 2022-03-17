#!/bin/bash
OUTPUT_TMP=`mktemp`
OUTPUT_FINAL=/data/tmp/.zurnal.mp3
URL_RANO=`curl -so - 'https://api.rtvs.sk/xml/applepodcast_archive.xml?series=1122' | grep mp3 | head -1 | sed -e 's/.*\(http.*mp3\).*/\1/g'`
URL_VECER=`curl -so - 'https://api.rtvs.sk/xml/applepodcast_archive.xml?series=1124' | grep mp3 | head -1 | sed -e 's/.*\(http.*mp3\).*/\1/g'`
URL_LATEST=`(echo $URL_RANO; echo $URL_VECER) | sort -n | tail -1`
LATEST_DOWNLOADED_FILE=/data/tmp/.latest_zurnal
LATEST_DOWNLOADED=""
if [ -f $LATEST_DOWNLOADED_FILE ]; then
    LATEST_DOWNLOADED=`cat $LATEST_DOWNLOADED_FILE`
    if [ "$LATEST_DOWNLOADED" == "$URL_LATEST" ]; then
        # already downloaded this one
        exit 0
    fi
fi
curl -so $OUTPUT_TMP "$URL_LATEST"
echo $URL_LATEST > $LATEST_DOWNLOADED_FILE
chmod a+r $OUTPUT_TMP
mv $OUTPUT_TMP $OUTPUT_FINAL
exit 0
