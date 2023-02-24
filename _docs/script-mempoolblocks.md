---
panelgroup: Bitcoin Panels
name: Mempool Blocks
title: Mempool Blocks Script
layout: default
---

# Mempool Blocks

This script prepares an image showing statistics about upcoming blocks in the
mempool.  Information about the size of the block, number of transactions, and
fee ranges are provided. It's useful to have this information when preparing a
layer 1 transaction to set fees based on your time preference.  It is based on
the appearance of the mempool space viewer at the publicly accessible
[mempool.space](https://mempool.space) website.  If you have your own MyNodeBTC
instance, or another popular node package running mempool service locally, you
can configure that instance instead for more privacy.  

![sample image of mempool blocks](../images/mempoolblocks.png)

## Script Location

The script is installed at 
[/home/nodeyez/nodeyez/scripts/mempoolblocks.py](../scripts/mempoolblocks.py).

## Configuration

To configure this script override the default configuration as follows

```shell
nano /home/nodeyez/nodeyez/config/mempoolblocks.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/mempoolblocks.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| urlmempool | The url for the mempool blocks information. If you are running your own mempool.space service on MyNodeBTC, then use http://127.0.0.1:4080/api/v1/fees/mempool-blocks. Default `https://mempool.space/api/v1/fees/mempool-blocks` |
| urlfeerecs | The url for the mempool fees recommendation. If you are running your own mempool.space service on MyNodeBTC, then use http://127.0.0.1:4080/api/v1/fees/recommended. Default `https://mempool.space/api/v1/fees/recommended` |
| urlfeehistogram | The url for the mempool fee histogram data. If you are running your own mempool.space service on MyNodeBTC, then use http://127.0.0.1:4080/api/mempool. Default `https://mempool.space/api/mempool` |
| useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
| colorBlockEdgeOutline | The color to use for the outline of block shapes expressed as a Hexadecimal color specifier. Default `#202020` |
| colorBlockSide | The color to use for the side of the block expressed as a Hexadecimal color specifier. Default `#404040` |
| colorBlockTop | The color to use for the top of the block expressed as a Hexadecimal color specifier. Default `#606060` |
| blockSatLevels | A array of one or more block sat level definitions to influence block color rendering by median sat/vB. The structure of a satlevel definition is defined below. |
| histogramSatLevels | An array of one or more histogram sat level definitions to show fee level histogram by sat/vB of transactions in the mempool. The structure is defined below. |
| blocksToRender | The maximum number (1-6) of upcoming blocks to render which will influence the size of the blocks drawn. Default `3` |
| renderStyle | The style to render the image. Options: `righttoleft`, `lefttoright`. Default: `righttoleft` |

__blockSatLevels__

| field name | description |
| --- | --- |
| satMin | The minimum sat/vbyte value to apply this colorset |
| satMax | The maximum sat/vbyte value to apply this colorset |
| colorBlock | The color to use for the face of the block when the sat/vbyte is within range of satMin-satMax |
| colorText | The color to use for the text of the block when the sat/vbyte is within range of satMin-satMax |

Default definition based on mempool.space

```json
blockSatLevels = [
  {"satMin": 0.0, "satMax": 10.0, "colorBlock": "#40c040", "colorText": "#ffffff"},
  {"satMin": 10.0, "satMax": 30.0, "colorBlock": "#9ea90b", "colorText": "#ffffff"},
  {"satMin": 30.0, "satMax": 60.0, "colorBlock": "#d1ac08", "colorText": "#ffffff"},
  {"satMin": 60.0, "satMax": 100.0, "colorBlock": "#f4511e", "colorText": "#ffffff"},
  {"satMin": 100.0, "satMax": 150.0, "colorBlock": "#b71c1c", "colorText": "#ffffff"},
  {"satMin": 150.0, "satMax": 9999.0, "colorBlock": "#4a148c", "colorText": "#ffffff"}
]
```

__histogramSatLevels__

| field name | description |
| --- | --- |
| satMin | The minimum sat/vbyte value to apply this colorset |
| satMax | The maximum sat/vbyte value to apply this colorset |
| colorFill | The color to use for the graph portion when the sat/vbyte is within range of satMin-satMax |

Default definition based on mempool.space

```json
histogramSatLevels: [
  {"satMin": 0.0, "satMax": 2.0, "colorFill": "#d81b60"},
  {"satMin": 2.0, "satMax": 3.0, "colorFill": "#8e24aa"},
  {"satMin": 3.0, "satMax": 4.0, "colorFill": "#5e35b1"},
  {"satMin": 4.0, "satMax": 5.0, "colorFill": "#3949ab"},
  {"satMin": 5.0, "satMax": 6.0, "colorFill": "#1e88e5"},
  {"satMin": 6.0, "satMax": 8.0, "colorFill": "#039be5"},
  {"satMin": 8.0, "satMax": 10.0, "colorFill": "#00acc1"},
  {"satMin": 10.0, "satMax": 12.0, "colorFill": "#00897b"},
  {"satMin": 12.0, "satMax": 15.0, "colorFill": "#43a047"},
  {"satMin": 15.0, "satMax": 20.0, "colorFill": "#7cb342"},
  {"satMin": 20.0, "satMax": 30.0, "colorFill": "#c0ca33"},
  {"satMin": 30.0, "satMax": 40.0, "colorFill": "#fdd835"},
  {"satMin": 40.0, "satMax": 50.0, "colorFill": "#ffb300"},
  {"satMin": 50.0, "satMax": 60.0, "colorFill": "#fb8c00"},
  {"satMin": 60.0, "satMax": 70.0, "colorFill": "#f4511e"},
  {"satMin": 70.0, "satMax": 80.0, "colorFill": "#6d4c41"},
  {"satMin": 80.0, "satMax": 90.0, "colorFill": "#757575"},
  {"satMin": 90.0, "satMax": 100.0, "colorFill": "#546e7a"},
  {"satMin": 100.0, "satMax": 125.0, "colorFill": "#b71c1c"},
  {"satMin": 125.0, "satMax": 150.0, "colorFill": "#880e4f"},
  {"satMin": 150.0, "satMax": 9999.0, "colorFill": "#4a148c"}
]
```

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

To run this script

```shell
cd /home/nodeyez/nodeyez/scripts
/usr/bin/env python3 mempoolblocks.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-mempoolblocks.service
sudo systemctl start nodeyez-mempoolblocks.service
```

---

[Home](../) | 

