---
title: Raspberry Pi Screen Attached to GPIO pins
---

# Display to a screen attached to GPIO pins

The Raspberry Pi is a great single board computer (SBC) that offers multiple
interfaces.  You can use the GPIO header pins to attach a premade display hat
for viewing images.  

This guide and the scripts focus on use of a 3.5" TFT screen with a resolution
of 480x320.  This size choice was made because existing raspiblitz project uses
this screen, and there are cases available from Cryptocloaks also making use of
these screens.  You can deviate and use a different size screen, but setting
up alternative displays are outside the scope of this guide.  Some scripts do
have some initial support for scaling to different resolutions

Most screens with a 480x320 resolution based on the XPT2046 chip should work.
These screen look like this

![image of the 3.5" TFT screen for raspberry pi](../images/xpt2046-tft-piscreen.jpg)

If you cannot get one at a local electronics store, you may be able to source
from amazon [here](https://www.amazon.com/gp/product/B07V9WW96D) 
  or [here](https://www.amazon.com/gp/product/B07L414LZP)
  or [here](https://www.amazon.com/gp/product/B08KZXSJW2)
  or [here](https://www.amazon.com/gp/product/B083C12N57).  

If you can't source one from any of the above, reach out to me on Twitter.
I have some extras that I can sell.

**To setup the screen**

## Login to your node

You will need to SSH into your node as a privileged user that can sudo

- MyNodeBTC: ssh as admin
- Raspiblitz ssh as admin
- Raspibolt: ssh as admin
- Umbrel: ssh as umbrel
- Default Raspbian: ssh as pi

## Raspberry Pi Config program

Access the raspberry pi config program as follows

```shell
sudo raspi-config
```

Choose the menu options for 
- Choice 3. Interface Options
- Choice P4 SPI.  

Note that the raspi-config program has changed over time and your menu
choices may differ. Ultimately, you're looking for the option to enable
SPI to support access to the display attached to the GPIO pins

Save and exit the raspi-config program


## Edit /boot/config.txt

Next, edit the /boot/config.txt file

```shell
sudo nano /boot/config.txt
```

Verify that it has a line reading `dtparam=spi=on`

You'll need to add a line at the bottom of the file for the screen as 
`dtoverlay=piscreen,speed=16000000,rotate=270`.  

The 270 rotation is a landscape mode with the ports for USB and ethernet to
the right.  

All images created by the scripts are in landscape mode, so you're rotation 
should be either 90 or 270 depending on preferred orientation.  

If you are using a [Lightning Shell case from Cryptocloaks](https://www.cryptocloaks.com/product/lightningshell/) and your lightning bolt is oriented...
- ...to the right side of the screen: `rotate=90`
- ...to the left side of the screen: `rotate=270`

![Image of the CryptoCloaks Lightning Shell Case](https://www.cryptocloaks.com/wp-content/uploads/2018/10/IMG_20200529_061711-e1590762533451.jpg)

Save (CTRL+O) and Exit (CTRL+X).

## Framebuffer Image Viewer

Don't be alarmed by the package name. This is a simple utility to send video bytes to the framebuffer associated with the screen device for display.

```shell
sudo apt-get -y install fbi
```

## Reboot

You'll need to reboot before the changes for boot and the GPIO pins are enabled for the screen.  

You should do a safe shutdown or reset. Don't simply turn off the power by flipping a switch or pulling the plug if you can avoid it.

If you're running a node package like MyNodeBTC or Umbrel etc., then use the web interface power cycle the device cleanly.

From the command line you can simply call `sudo init 6`


## Log Back In

After waiting for the pi to restart, log to your node with the same user

## Quick Test

Do a quick test to verify that the screen can display an image.

We'll download an image from Nodeyez github repo, and then display it to the screen

```shell
cd /tmp
wget https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/logo.png
sudo fbi --vt 1 --autozoom --device /dev/fb0 -1 logo.png
rm logo.png
```

You should see the picture of eyes as depicted below.  If you don't see this recheck your progress through the steps above.
In rare situations, you may need to adjust the value of `--vt` (try `0`) or `--device` (try `/dev/fb1`).  If for some reason
you do have to make changes here, make note of them as you'll need to make similar modifications to the slideshow.sh file.


![nodeyez logo](../images/logo.png)   

---

[Home](../README.md) | [Back to Python and Dependencies](./install-2-pythondeps.md) | [Continue to Nodeyez](./install-4-nodeyez.md)

