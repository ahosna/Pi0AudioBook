#!/bin/bash

SEGMENT_TIME=600
TITLES_DIR=~/code/Pi0AudioBook/chapters

if [ "$1" == "" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: <output_directory> <input_file 1> [input_file 2] [...]"
    echo "Use input files to produce audio chapters with names 0001.mp3, 0002.mp3, ..."
    echo "in the output directory. Output_directory is created at the startup."
    echo "$TITLES_DIR must exist and have chaper files 0001.mp3, 0002.mp3, ..."
    echo "Chapter heading can be any audio track that will get prepended to coresponding chapter."
    exit 1
fi 

ffmpeg --help > /dev/null 2>&1 
if [ $? -ne 0 ]; then
    echo "You need ffmpeg with LAME plugins to use this script"
    exit 1
fi

main_dir=$1
shift


# create dir if it does not exist
mkdir -p "$main_dir"

c=1;
for f in "$@"; do
    split_dir=$(printf "%s/%04d" "$main_dir" $c)
    mkdir -p "$split_dir"
    # -q:a 6 is vbr ~ 128
    ffmpeg -i "$f" -f segment -segment_time $SEGMENT_TIME -q:a 6 "$split_dir/%04d.mp3"
    c=$((c+1))
done

chapters=`find $main_dir -type f -name \*.mp3 | sort`
d=1;
for chap in $chapters; do 
    output=$(printf "%s/%04d.mp3" "$main_dir" $d) 
    title=$(printf "%s/%04d.mp3" "$TITLES_DIR" $d)
    ffmpeg -i "$title" -i "$chap" -filter_complex '[0:0][1:0]concat=n=2:v=0:a=1[out]' -map '[out]' "$output"
    d=$((d+1))
done

find "$main_dir" -type d -depth 1 | while read d; do 
    rm -fr $d
done

