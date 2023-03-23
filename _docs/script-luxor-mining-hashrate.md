---
panelgroup: Mining Panels
name: Luxor Mining Hashrate
title: Luxor Mining Hashrate Script
layout: default
description: Creates images for each month of hashrate data available for Luxor mining pool account
imageurl: ../images/luxor-mining-hashrate-2021-12.png
---

# Luxor Mining Hashrate

This script prepares images for each month of hashrate data available for your
Luxor Tech mining pool account.

![sample image of luxor hashrate for a month](../images/luxor-mining-hashrate-2021-12.png)

Status: Beta. 

See also the [../scripts/daily-data-retrieval.py](../scripts/daily-data-retrieval.py)
script and [documentation](./script-daily-data-retrieval.md) which retrieves the
same information but doesn't produce the images. In time this script will be
updated to use that common data.

## Script Location

The script is installed at
[~/nodeyez/scripts/luxor-mining-hashrate.py](../scripts/luxor-mining-hashrate.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/luxor.json` file

Fields are defined below

- You must have an account with [Luxor](https://beta.luxor.tech/) and an
  API Key for that account. Read only access is sufficient

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/luxor-mining-hashrate.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `86400` |
| apikey | Your api key for your Luxor account. |
| username | Your username for your Luxor account. |
| subheadingText | A label beneath the main header useful for identifying the miner. Default `S19 Pro 110TH` |
| hashrateTarget | The hashrate per second for the expected miner output. Default `110000000000000` |
| hashrateLowThreshold | The hashrate level for which hashing should be considered low. Default `90000000000000` | 
| colorDataValue | The color of the text values for major categories expressed as a Hexadecimal color specifier. Default `#4040ff` | 
| colorHashDotFill | The color to plot a dot for the hashrate when normal at a point in time expressed as a Hexadecimal color specifier. Default `#4040ff` |
| colorHashDotFillZero | The color to plot a dot for the hashrate when it is zero/unreported at a point in time expressed as a Hexadecimal color specifier. Default `#ff4040` |
| colorHashDotFillLow | The color to plot a dot for the hashrate when it below the low threshold at a point in time expressed as a Hexadecimal color specifier. Default `#ffff40` |
| colorHashDotOutline | The color to make the outline of plotted dots for normal hashrate expressed as a Hexadecimal color specifier. Default `#0000ff` |
| colorHashDotOutlineZero | The color to make the outline of plotted dots for zero/unreported hashrate expressed as a Hexadecimal color specifier. Default `#ff0000` | 
| colorHashDotOutlineLow | The color to make the outline of plotted dots for low hashrate expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorMovingAverage | The color to use for the moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorGraphLineLight | The color to use for the left and bottom borders of the plot graph, expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
| colorGraphLineDark | The color to use for the right and top borders of the blot graph, expressed as a Hexadecimal color specifier. Default `#606060` |

## Run Directly

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
python luxor-mining-hashrate.py
```

Press CTRL+C to stop the process

## Run at Startup

There is currently no service script defined for this script to run at startup

---

[Home](../) | 