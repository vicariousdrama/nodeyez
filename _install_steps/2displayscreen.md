---
name: Display Screen
title: NODEYEZ Display Screen for Raspberry Pi
layout: default
---

# Display to an Attached Screen

This step is optional. 

If you are not using a Raspberry Pi, or you don't want to attach a screen to
your Raspberry Pi, then you can proceed with the next section:
[Python and Dependencies](./install-3-pythondeps.md)

If you later choose to add a screen to your Raspberry Pi, you can come back
and do this step later.

The Raspberry Pi is a great single board computer (SBC) that offers multiple
interfaces.

- GPIO Pin connection to easily attach premade screens on top
- MIPI DSI Display connector for smaller screens using a 15 pin flexible ribbon
  cable
- Micro HDMI where you use an adapter to connect to a PC monitor or television

Regardless of which option you choose, to display images you'll need to log
into your node and install the framebuffer image viewr package.

## Login to your node

You will need to SSH into your node as a privileged user that can sudo

- MyNodeBTC: ssh as admin
- Raspiblitz ssh as admin
- Raspibolt: ssh as admin
- Umbrel: ssh as umbrel
- Default Raspbian: ssh as pi

## Framebuffer Image Viewer

Don't be alarmed by the package name. This is a simple utility to send video
bytes to the framebuffer associated with the screen device for display.

```shell
sudo apt-get -y install fbi
```

## Using GPIO Screen

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

If you can't source one from any of the above, reach out to me on 
[Twitter](https://twitter.com/vicariousdrama) or [Nostr]
I have some extras that I can sell.

**To setup the screen**

### Raspberry Pi Config program

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

### Edit /boot/config.txt

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


### Reboot

You'll need to reboot before the changes for boot and the GPIO pins are enabled for the screen.  

You should do a safe shutdown or reset. Don't simply turn off the power by flipping a switch or pulling the plug if you can avoid it.

If you're running a node package like MyNodeBTC or Umbrel etc., then use the web interface power cycle the device cleanly.

From the command line you can simply call `sudo init 6`

After waiting for the pi to restart, log to your node with the same user.  Proceed with the [Quick Text](#quicktest) section


## Using DSI Screen

The Display Serial Interface (DSI) connector is a small connector on the side
opposite the USB and Ethernet ports on a Raspberry Pi.  Though screens that use
this interface tend to cost more, there are significant advantages in this
approach

- The interface is high speed compared to using the GPIO pins
- It frees up the GPIO pins to attach a fan
- The flexible ribbon cable (FRC) allows more versatility in where the screen is
  ultimately placed, and can be acquired in a variety of lengths.

I only have experience working with the [800x480 DSI screen](https://www.amazon.com/dp/B091FYFNV8),
which I've mounted on my setup in portrait orientation.  This allows me to
display 2 of the images created by Nodeyez scripts simultaneously using the
[Nodeyez Dual](./script-nodeyezdual.md) script. 

Regardless of which DSI screen you choose, consider picking up an 
[assortment of ribbon lengths](https://www.amazon.com/dp/B08662272F) unless you
know exactly what length you require.

**To setup the screen**

### Edit /boot/config.txt

Next, edit the /boot/config.txt file

```shell
sudo nano /boot/config.txt
```

Comment out the following lines by putting a # mark at the beginning of the line

```c
# camera_auto_detect=1
# dtoverlay=vc4-kms-v3d
```

You can optionally disable the standard splash screen on bootup

```c
disable_splash=1
```

Then add this section to the bottom

```c
[all]
# Enable Display for 5 inch LCD
dtoverlay=vc4-kms-DPI-5inch,backlight-def-brightness=2
display_rotate=3
dtoverlay=rpi-backlight
```

You may prefer a different value for `display_rotate` depending on the orientation
you choose for your display
- display_rotate=0: standard
- display_rotate=1: 90 degrees
- display_rotate=2: 180 degrees
- display_rotate=3: 270 degrees

Save (CTRL+O) and Exit (CTRL+X).

### Install Overlay File

This screen is using a custom overlay. Download and install into the overlays
folder following these commands.

```shell
cd /tmp
wget https://www.waveshare.net/w/upload/8/86/vc4-kms-DPI-5inch.dtbo
sudo mv vc4-kms-DPI-5inch.dtbo /boot/overlays/vc4-kms-DPI-5inch.dtbo
```

### Reboot

You'll need to reboot before the changes to use the new overlay driver take effect.

You should do a safe shutdown or reset. Don't simply turn off the power by flipping a switch or pulling the plug if you can avoid it.

If you're running a node package like MyNodeBTC or Umbrel etc., then use the web interface power cycle the device cleanly.

From the command line you can simply call `sudo init 6`

After waiting for the pi to restart, log to your node with the same user.  Proceed with the [Quick Text](#quicktest) section


## Using HDMI

The High Definition Multimedia Inteface (HDMI) is a very common interface now.
To use it with the Raspberry Pi, you'll need a micro HDMI to HDMI cable, or a
standard HDMI to HDMI cable plus a micro HDMI to HDMI adapter.


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

[Home](../) | [Back to Your Node]({% link _install_steps/1yournode.md %}) | [Continue to Tools]({% link _install_steps/3tools.md %})
