#!/bin/bash

ROUTER="192.168.1.1"
INTERFACE="wlan0"
INTERVAL=1


while /bin/sleep $INTERVAL; do
    #/sbin/ping "$ROUTER" -c 10 -i 0.5 -W 0.5 | grep "bytes from" > /dev/null 2>&1  # OSX
    /sbin/ping "$ROUTER" -i 0.5 -w 5 | grep "bytes from" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        /usr/bin/logger "Can't ping the uplink $ROUTER. Restarting $INTERFACE"
        /sbin/ifdown $INTERFACE
        /bin/sleep 5
        /sbin/ifup $INTERFACE
    else
        /usr/bin/logger "Router is pingable. Everything is fine."
    fi
done

