---
panelgroup: Bitcoin Panels
name: Block Stats
title: Block Stats for Bitcoin
layout: default
description: Renders an image of stats for the current block height including inputs, outputs, transaction count, percentage of segwit, the size of the block and utxo set change, fee rates and fees for transactions. Optionally renders time series data for fee rates and segwit
images:
    - ../images/blockstats.png
    - ../images/blockstats-feerates.png
    - ../images/blockstats-segwit.png
---

# Block Stats

This script prepares an image displaying stats for the current or specified block height.  
It depends on a bitcoin node running locally and fully synched.

![sample image of stats for block 7779148](../images/blockstats.png)

An additional image can be produced to graph fee rates over time

![sample image of fee rates from block 778668 to 779148](../images/blockstats-feerates.png)

An additional image can be produced to graph segwit prevalence over time

![sample image of segwit prevalence from block 778668 to 779148](../images/blockstats-segwit.png)

## Script Location

The script is installed at 
[../scripts/blockstats.py](../scripts/blockstats.py).

## Configuration

To configure this script override the default configuration as follows

```shell
nano ../config/blockstats.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Optional additional images use a suffix based on this name. Default `../imageoutput/blockstats.png` |
| dataDirectory | The base path for the directory to store saved files. This helps improve performance as a file is used to cache blockstats data. Default `../data/` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| colorShapeOutline | The color to use for outlining the blockstats image charts. Default `#888888` |
| colorShapeShadow | The color to use for shadow of the blockstats image. Default `#88888888` |
| colorGraphOutline | The color to use for outlining charts and their labels. Default `#888888` |
| colorGraphValue | The color to use for primary value in chart for fee rates. Default `#FF8888` |
| colorGraphAverage | The color to use for the average value line drawn across fee rates. Default `#8888FF` |
| colorBands | An array of colors to use for multi valued charts. Default: `#FFFF00`, `#0000FF`, `#00FF00`, `#808000`, `#FF0000`, `#00FFFF`, `#800000`, `#808080`, `#008000`, `#800080`, `#FF00FF`, `#008080` |
| logStatsForRanges | Indicates whether summary stats should be reported to log output. Default: `true` |
| showStatsBlock | Indicates whether the stats block image should be created. Default: `true` |
| showFeeRates | Indicates whether the fee rates image should be created. Default: `true` |
| showSegwitPrevalence | Indicates whether the segwit prevalence image should be created. Default `true` |


After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Running Directly

To run this script

```shell
cd ../scripts
/usr/bin/env python3 blockstats.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-blockstats.service
sudo systemctl start nodeyez-blockstats.service
```


---

[Home](../) | 

