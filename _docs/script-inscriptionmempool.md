# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## Unmined Inscriptions in Mempool

This script calls your local bitcoin node and will analyze your view of the mempool to
identify and extract inscriptions found in transactions.  A summary image of the most
recent inscriptions will be generated as the output file.

- For more information about Ordinals, checkout the [Ordinals Website](https://docs.ordinals.com/).
- For more information about Inscriptions, checkout the [Inscriptions section](https://docs.ordinals.com/inscriptions.html).
- For more technical explanation of OP codes used by this script for parsing out the Ordinal Inscriptions, see the [Script Wiki Page](https://en.bitcoin.it/wiki/Script)

![sample inscription mempool](../images/inscriptionmempool.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /usr/bin/env python3 inscriptionmempool.py
   ```

   Press CTRL+C to stop the process

   This script also supports optional command line arguments for a single run and exit.

   1. Pass the desired width and height as arguments as follows

   ```sh
   /usr/bin/env python3 inscriptionmempool.py 1920 1080
   ```


* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/inscriptionmempool.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/inscriptionmempool.png` |
   | dataDirectory | The path to store extracted files. A subfolder for ordinals will be created if it doesnt exist. Default `/home/nodeyez/nodeyez/data/` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `10` |
   | colorTextFG | The color to use for the header expressed as a hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../) | 

