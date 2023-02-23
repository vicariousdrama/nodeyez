# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## Fear and Greed Index

This script can use previously retrieved data for the Fear and Greed index as
determined and made available by alternative.me.  A graph of the trend over
time is depicted as well as displaying the current level and descriptor at
the top of the image.

![sample image of fear and greed index](../images/fearandgreed.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /usr/bin/env python3 fearandgreed.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/fearandgreed.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/fearandgreed.png` |
   | useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
   | url | The url that provides the fear and greed information. Default `https://api.alternative.me/fng/?limit=0&format=json&date_format=cn` |
   | dataDirectory | The path to store downloaded files. A subfolder for caching fearandgreed resources will be created if its doesn't exist. Default `/home/nodeyez/nodeyez/data/` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `43200` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | colorDataValue | The color of the data values for each entry expressed as a Hexadecimal color specifier. Default `#ff7f00` |
   | colorMovingAverage | The color to use for the moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
   | colorGraphLineLight | The color to draw the left and bottom of the graph outline expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
   | colorGraphLineDark | The color to draw the top and right and background dashed lines of the graph outline expressed as a Hexadecimal color specifier. Default `#606060` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |


   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

