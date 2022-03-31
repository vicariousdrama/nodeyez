#!/usr/bin/env bash

# the framebuffer image viewer (fbi) needs root so run this script with sudo
# install fbi via  `sudo apt-get -y install fbi`
foldertodisplay="/home/nodeyez/nodeyez/imageoutput"
timeperimage=5
while true
do
    imagecount=`ls ${foldertodisplay} | wc -l`
    sleepytime=$(($imagecount * $timeperimage))
    if [ ${sleepytime} -gt 0 ]; then
        fbi --vt 1 --autozoom --timeout ${timeperimage} --device /dev/fb0 --noreadahead --cachemem 0 --noverbose --norandom ${foldertodisplay}/* > /dev/null 2>&1
        sleep ${sleepytime}
        killall fbi > /dev/null 2>&1
    else
        sleep 15
    fi
done
