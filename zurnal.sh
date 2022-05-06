#!/bin/bash
OUTPUT_TMP=`mktemp`
OUTPUT_FINAL=/data/tmp/.zurnal.mp3
IDS=(1122 1123 1124 1125) # 0700, 1000, 1800, 2200
URL_BASE="https://api.rtvs.sk/xml/applepodcast_archive.xml?series="
for id in ${IDS[@]}; do
    url="https://api.rtvs.sk/xml/applepodcast_archive.xml?series=$id"
    data=`curl -so - $url | egrep 'mp3|pubDate' | head -2 | sed -e 's/.*\(http.*mp3\).*/\1/g' | sed -e 's/.*Date>\(.*\)<.*/\1/g' | tr "\n" ' '`
    if [ "$data" == "" ]; then
        continue
    fi
    # hackery to get the timestamp from pubDate and get latest
    d=${data#* }
    ts=`date -j -f '%a, %d %b %Y %H:%M:%S %z' "$d" '+%s' 2>/dev/null`
    echo $ts ${data%% *}
done | sort -nrk 1 | head -1 | cut -d " " -f 2| while read URL_LATEST; do
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
done
exit 0
