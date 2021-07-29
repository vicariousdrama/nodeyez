#!/bin/bash

# the framebuffer image viewer (fbi) needs root so run this script with sudo
# install fbi via  `sudo apt-get -y install fbi`
while true
do
    fbi --vt 1 --autozoom --timeout 5 --device /dev/fb0 --noreadahead --cachemem 0 --noverbose --norandom /home/admin/images/* > /dev/null 2>&1
    sleep 120
    killall fbi > /dev/null 2>&1
done
