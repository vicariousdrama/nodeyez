# ![Nodeyez](../../../raw/branch/main/images/nodeyez.svg)
Display panels to get the most from your node

## Channel Fees

This script prepares an image depicting your node's lightning channel routing
velocity and earned fees.  This is initially a basic table listing and will
likely evolve in the future.  Multiple images may be created depending on the
number of open channels.  The script is installed at [/home/nodeyez/nodeyez/scripts/channelfees.py](../scripts/channelfees.py).
It depends on a lighting node.

![sample image of channel balance](../images/channelfees.png)


* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/channelfees.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/channelfees.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/channelfees.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `1800` |
   | pageSize | The number of channels to represent per page rendered. Default `8` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

---

[Home](../README.md) | 

