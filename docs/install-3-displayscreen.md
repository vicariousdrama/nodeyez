# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Display to a screen attached to GPIO pins

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

1. While still logged in as a privileged user, enter the raspberry pi config 
   program

   ```sh
   sudo raspi-config
   ```

   Choose the menu options for 
     - 3. Interface Options
     - P4 SPI.  

   Note that the raspi-config program has changed over time and your menu
   choices may differ. Ultimately, you're looking for the option to enable
   SPI to support access to the display attached to the GPIO pins

   Save and exit the raspi-config program

2. Edit the /boot/config.txt file

   ```sh
   sudo nano /boot/config.txt
   ```

   Verify that it has a line reading `dtparam=spi=on`

   You'll need to add a line at the bottom of the file for the screen as 
   `dtoverlay=piscreen,speed=16000000,rotate=270`.  

   The 270 rotation is a landscape mode with the ports for USB and ethernet to
   the right.  

   All images created by the scripts are in landscape mode, so you're rotation 
   should be either 90 or 270 depending on preferred orientation.  

   If you are using a Lightning Shell case from Cryptocloaks 
   - and your lightning bolt is on the right side of the screen: rotate=90
   - and your lightning bolt is on the left side of the screen: rotate=270

   Save (CTRL+O) and Exit (CTRL+X).

3. Next, install the framebuffer image viewer 

   ```sh
   sudo apt-get -y install fbi
   ```

4. Reboot. You'll need to reboot before the changes for boot and the GPIO pins
   are enabled for the screen.  

   You should do a safe shutdown or reset. Don't simply turn off the power by
   flipping a switch or pulling the plug if you can avoid it.

   If you're running a node package like MyNodeBTC, then use the web interface
   power cycle the device cleanly.  

   From the command line you can use `sudo init 6`.

   Once the raspberry pi has rebooted, log back in as the privileged user

5. Do a quick test to verify that the screen can display an image

   ```sh
   (
   cd /tmp
   wget https://raw.githubusercontent.com/vicariousdrama/nodeyez/fix-div-by-zero/images/logo.png
   sudo fbi --vt 1 --autozoom --device /dev/fb0 -1 logo.png
   rm logo.png
   )
   ```

---

[Home](../README.md) | [Back to Python and Library Dependencies](./install-2-pythonlibs.md) | [Continue to Nodeyez](./install-4-nodeyez.md)

