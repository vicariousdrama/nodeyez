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
It depends on a bitcoin node.

![sample image of stats for block 7779148](../images/blockstats.png)

An additional image can be produced to graph fee rates over time

![sample image of fee rates from block 778668 to 779148](../images/blockstats-feerates.png)

An additional image can be produced to graph segwit prevalence over time

![sample image of segwit prevalence from block 778668 to 779148](../images/blockstats-segwit.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/blockstats.py](../scripts/blockstats.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/blockstats.json` file

Fields are defined below

| field name | description |
| --- | --- |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| graphAverageColor | The color to use for the average value line drawn across fee rates. Default `#8888FF` |
| graphBorderColor | The color to use for outlining charts and their labels. Default `#888888` |
| graphDataColors | An array of colors to use for multi valued charts. Default: `#FFFF00`, `#0000FF`, `#00FF00`, `#808000`, `#FF0000`, `#00FFFF`, `#800000`, `#808080`, `#008000`, `#800080`, `#FF00FF`, `#008080` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| renderStatsImage | Indicates whether the stats block image should be created. Default: `true` |
| renderFeesImage | Indicates whether the fee rates image should be created. Default: `true` |
| renderSegwitImage | Indicates whether the segwit prevalence image should be created. Default `true` |
| renderScriptImage | Indicates whether images for script types should be rendered. Default `false` |
| reportStatsEnabled | Indicates whether summary stats should be reported to log output. Default: `true` |
| shapeOutlineColor | The color to use for outlining the blockstats image charts. Default `#888888` |
| shapeShadowColor | The color to use for shadow of the blockstats image. Default `#88888888` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| width | The width, in pixels, to generate the image. Default `480` |

## Running Directly

Ensure the virtual environment is activated
```shell
source ~/.pyenv/nodeyez/bin/activate
```

Change to the scripts folder
```shell
cd ~/nodeyez/scripts
```

Run it
```shell
python blockstats.py
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