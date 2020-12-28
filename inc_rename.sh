#!/bin/bash

#params format like "x%04d.mp3"
if [ "$1" == "" ]; then
    echo "Usage $0 <format_string>"
    echo "Example: 'file%04d.mp3' renames all files in the local directory"
    echo "sequentially to file0001.mp3, file0002.mp3, file0003.mp3, ..."
    exit 1
fi

IFS='
'
c=1
files=`ls -1 .`
for f in $files; do
    n=`printf $1 $c`
    mv "$f" "$n"
    c=$((c+1))
done 
