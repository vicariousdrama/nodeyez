# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Mempool Blocks

This script prepares an image showing statistics about upcoming blocks in the
mempool.  Information about the size of the block, number of transactions, and
fee ranges are provided. It's useful to have this information when preparing a
layer 1 transaction to set fees based on your time preference.  It is based on
the appearance of the mempool space viewer at the publicly accessible
[mempool.space](https://mempool.space) website.  If you have your own MyNodeBTC
instance, or another popular node package running mempool service locally, you
can configure that instance instead for more privacy.  The script is installed
at [/home/nodeyez/nodeyez/scripts/mempoolblocks.py](../scripts/mempoolblocks.py).

![sample image of mempool blocks](../images/mempoolblocks.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   ./mempoolblocks.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/mempoolblocks.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/mempoolblocks.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
   | urlmempool | The url for the mempool blocks information. If you are running your own mempool.space service on MyNodeBTC, then use http://127.0.0.1:4080/api/v1/fees/mempool-blocks. Default `https://mempool.space/api/v1/fees/mempool-blocks` |
   | urlfeerecs | The url for the mempool fees recommendation. If you are running your own mempool.space service on MyNodeBTC, then use http://127.0.0.1:4080/api/v1/fees/recommended. Default `https://mempool.space/api/v1/fees/recommended` |
   | colorBlockEdgeOutline | The color to use for the outline of block shapes expressed as a Hexadecimal color specifier. Default `#202020` |
   | colorBlockSide | The color to use for the side of the block expressed as a Hexadecimal color specifier. Default `#404040` |
   | colorBlockTop | The color to use for the top of the block expressed as a Hexadecimal color specifier. Default `#606060` |
   | satLevel1 | The recommended fee level to render blocks with colorBlock1 as sats per vbyte. Default `10` |
   | satLevel2 | The recommended fee level to render blocks with colorBlock2 as sats per vbyte. Default `30` |
   | satLevel3 | The recommended fee level to render blocks with colorBlock3 as sats per vbyte. Default `60` |
   | satLevel4 | The recommended fee level to render blocks with colorBlock4 as sats per vbyte. Default `100` |
   | satLevel5 | The recommended fee level to render blocks with colorBlock5 as sats per vbyte. Default `150` |
   | colorBlock0 | The default color to use for the face of the block expressed as a Hexadecimal color specifier. Default `#40c040` |
   | colorBlock1 | The color to use for blocks higher where recommended fee is higher than satLevel1 expressed as a Hexadecimal color specifier. Default `#c0ca33` |
   | colorBlock2 | The color to use for blocks higher where recommended fee is higher than satLevel2 expressed as a Hexadecimal color specifier. Default `#fdd83f` |
   | colorBlock3 | The color to use for blocks higher where recommended fee is higher than satLevel3 expressed as a Hexadecimal color specifier. Default `#f4511e` |
   | colorBlock4 | The color to use for blocks higher where recommended fee is higher than satLevel4 expressed as a Hexadecimal color specifier. Default `#b71c1c` |
   | colorBlock5 | The color to use for blocks higher where recommended fee is higher than satLevel5 expressed as a Hexadecimal color specifier. Default `#4a148c` |
   | blocksToRender | The maximum number (1-6) of upcoming blocks to render which will influence the size of the blocks drawn. Default `3` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

