# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## Ordinal Inscriptions

This script calls your local bitcoin node and will look for any transaction entries
where the input data matches the structure of Ordinal Inscriptions.  It will then 
parse out the data, and for each image will prepare a display image wrapper depicting
the image, the block, and the txid.

- For more information about Ordinals, checkout the [Ordinals Website](https://docs.ordinals.com/).
- For more information about Inscriptions, checkout the [Inscriptions section](https://docs.ordinals.com/inscriptions.html).
- For more technical explanation of OP codes used by this script for parsing out the Ordinal Inscriptions, see the [Script Wiki Page](https://en.bitcoin.it/wiki/Script)

![sample ordinal display](../images/ordinals.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /usr/bin/env python3 ordinals.py
   ```

   Press CTRL+C to stop the process

   This script also supports optional command line arguments for a single run and exit.

   1. Pass the desired block number or range as an argument as follows

   ```sh
   /usr/bin/env python3 ordinals.py 773046
   # or
   /usr/bin/env python3 ordinals.py 775000-775100
   ```


   2. Pass the desired block number or range, width and height as arguments

   ```sh
   /usr/bin/env python3 ordinals.py 774411 800 600
   # or
   /usr/bin/env python3 ordinals.py 775123-775223 1920 1080
   ```


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
   | dataDirectory | The path to store extracted files. A subfolder for ordinals will be created if it doesnt exist. Default `/home/nodeyez/nodeyez/data/` |
   | exportFilesToDataDirectory | Indicates whether files should be exported to the data directory. Default `true` |
   | saveUniqueImageNames | Indicates whether unique image names should be created for each inscription. Default `true` |
   | overlayTextEnabled | Indicates whether annotations should be labeled over the image to display the transaction id, content type and size information. Default `true` |
   | overlayExifEnabled | Indicates whether key exif data found in images should be labeled over the image in the annotation block. Default `true` |
   | overlayTextBG | If overlayTextEnabled is true, this is the color of the annotation text background overlay expressed as a Hexadecimal color specifier. Default `#00000080` |
   | overlayTextFG | If overlayTextEnabled is true, this is the color of the annotation text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | uniqueOutputFile | The path to save individual generated images for each inscription. This is a base path where the block number and index of the transaction in the block will be included at the end of the file name but before the extension. Default `/home/nodeyez/nodeyez/imageoutput/ordinals/ordinals.png` |
   | blocklistURL | An optional URL to a resource that provides a list of block inscriptions not to extract. Default `https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/sample-config/ordblocklist.json` |
   | useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 
