# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## Ordinals

This script calls your local bitcoin node and will look for any transaction entries
where the input data matches the structure of Ordinal Inscriptions.  It will then 
parse out the data, and for each image will prepare a display image wrapper depicting
the image, the block, and the txid

![sample ordinal display](../images/ordinals.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/ordinals.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/ordinals.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/ordinals.png` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
   | colorTextFG | The color to use for the header expressed as a hexadecimal color specifier. Default `#ffffff` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

