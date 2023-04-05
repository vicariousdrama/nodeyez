#!/usr/bin/env bash

# the framebuffer image viewer (fbi) needs root so run this script with sudo
# install fbi via  `sudo apt-get -y install fbi`

# normally we rotate through all images that are produced in the folder
globtodisplay="../imageoutput/*.png"
timeperimage=3

# if nodeyezdual is active, only show that image
if [ $(systemctl show nodeyez-nodeyezdual | grep ActiveState=active | wc -l) -gt 0 ]; then
  globtodisplay="../imageoutput/nodeyezdual.png"
  timeperimage=30
fi

# start the loop
while true
do
    imagecount=`ls ${globtodisplay} | wc -l`
    sleepytime=$(($imagecount * $timeperimage))
    if [ ${sleepytime} -gt 0 ]; then
        fbi --vt 1 --autozoom --timeout ${timeperimage} --device /dev/fb0 --noreadahead --cachemem 0 --noverbose --norandom ${globtodisplay} > /dev/null 2>&1
        sleep ${sleepytime}
        killall fbi > /dev/null 2>&1
    else
        sleep 15
    fi
done
