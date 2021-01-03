#!/bin/bash

## include in /etc/rc.local with . /home/pi/Pi0AudioBook/knihaui-init.sh

# disable HDMI output
/usr/bin/tvservice -o
# Set volume to full blast
/usr/bin/amixer sset 'PCM' '100%'

# set permissions on /data do that mpd can read
/bin/chmod -R a+x /data

# Input PINs
/usr/bin/gpio mode 12 in
/usr/bin/gpio mode 13 in
/usr/bin/gpio mode 14 in

# Status indicator LED
/usr/bin/gpio mode 5 out
/usr/bin/gpio write 5 0
