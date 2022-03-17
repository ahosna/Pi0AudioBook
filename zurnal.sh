#!/bin/bash
OUTPUT_TMP=`mktemp`
OUTPUT_FINAL=/data/tmp/.zurnal.mp3
URL_RANO=`curl -so - 'https://api.rtvs.sk/xml/applepodcast_archive.xml?series=1122' | grep mp3 | head -1 | sed -e 's/.*\(http.*mp3\).*/\1/g'`
URL_VECER=`curl -so - 'https://api.rtvs.sk/xml/applepodcast_archive.xml?series=1124' | grep mp3 | head -1 | sed -e 's/.*\(http.*mp3\).*/\1/g'`

H=`date +%k | tr -d ' '`
if [ $H -ge 18 ] || [ $H -le 6 ]; then
    curl -so $OUTPUT_TMP "$URL_VECER"
else
    curl -so $OUTPUT_TMP "$URL_RANO"
fi
chmod a+r $OUTPUT_TMP
mv $OUTPUT_TMP $OUTPUT_FINAL
exit 0
