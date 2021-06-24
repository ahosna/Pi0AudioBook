#!/bin/bash

## include in /etc/rc.local with . /home/pi/Pi0AudioBook/knihaui-init.sh

# disable HDMI output
/usr/bin/tvservice -o
# Set volume to full blast
/usr/bin/amixer -c0 sset 'PCM' '100%'

# set permissions on /data do that mpd can read
/bin/chmod -R a+x /data

# PINs setup
# Input rotary encoder
/usr/bin/raspi-gpio set 19 ip pn
/usr/bin/raspi-gpio set 26 ip pn
# input buttons
/usr/bin/raspi-gpio set 5 ip pn
/usr/bin/raspi-gpio set 6 ip pn
/usr/bin/raspi-gpio set 13 ip pn
# Status indicator
/usr/bin/raspi-gpio set 4 op pn dh
