# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Channel Balance

This script prepares an image depicting your node's lightning channel balances.
Bar graphs show relative percentage of the channel balance on your end or the
remote. Multiple images may be created depending on the number of open channels.
The script is installed at [/home/nodeyez/nodeyez/scripts/channelbalance.py](../scripts/channelbalance.py).
It depends on a lighting node.

![sample image of channel balance](../images/channelbalance.png)


* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/channelbalance.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/channelbalance.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/channelbalance.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | colorBarOutline | The color of the outline for the channel balance bar expressed as a hexadecimal color specifier. Default `#770044` |
   | colorBarFilled | The color of the filled portion representing the local balance of the channel expressed as a hexadecimal color specifier. Default `#aa3377` |
   | colorBarEmpty | The color of the unfilled portion representing the remote balance of the channel expressed as a hexadecimal color specifier. Default `#202020` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `1800` |
   | pageSize | The number of channels to represent per page rendered. Default `8` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

---

[Home](../README.md) | 

