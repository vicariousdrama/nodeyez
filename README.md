# nodeyez
Display panels to get the most from your node

## Pre-requisites

1. Build yourself a Raspberry Pi Bitcoin Node.  
Consider following the helpful guidance at [node.guide](https://node.guide) on different nodes available.  Personally I like [Stadicus Raspibolt](https://github.com/Stadicus/RaspiBolt) and [MyNodeBTC](https://github.com/mynodebtc/mynode), but nearly any Raspberry Pi based node should be sufficient provided you have access to the GPIO pins.

2. Acquire and install a 3.5" TFT screen
The resolution is 480x320 and should be based on the XPT2046 chip.  The one I've used I got from a local electronics store.

3. Enable the GPIO for SPI. 
Login to your pi, and do `sudo raspi-config` (menu 3 Interface Options / P4 SPI). Save and exit.

4. Edit /boot/config.txt
```sh
sudo nano /boot/config.txt
```
You'll want to verify that it has `dtparam=spi=on`
Add a line at the bottom to set `dtoverlay=piscreen,speed=16000000,rotate=270`
The rotation should be 0, 90, 180, or 270 based on how you've oriented your screen. For reference, I have mine hanging on a wall with the USB and ethernet port to the right.

5. Install framebuffer image viewer
This is pretty straightforward. Just do 
```sh
sudo apt-get install fbi
```

6. Install Python
Raspberry Pi should come with Python 2.7 but will assume using Python3 in this guide. Go ahead and install with the following
```sh
sudo apt-get install python3
```

7. Install the Python Pillow library
These scripts were created with the newer Pillow library, but may work with PIL as well. Its my understanding that you can't install both. So its worth doing a check before installing.  See if pil or pillow is installed
`pip list | grep --ignore-case pi`
sample output
```sh
googleapis-common-protos 1.52.0
Pillow                   8.3.1
pip                      21.2.1
pipenv                   2020.6.2
RPi.GPIO                 0.7.0
typing-extensions        3.7.4.2
```
If neither PIL or Pillow is installed, then go ahead with
`pip install Pillow`

8. Reboot
You'll need to reboot before the changes for boot and the GPIO pins are enabled for the screen.  Do a safe shutdown. If you're running a node package like MyNodeBTC, then use the console to power cycle the device cleanly.  

## blockheight.py
This python script will query the local bitcoin node using bitcoin-cli and prepare an image representing the block height

![alt text](./blockheight.png)
