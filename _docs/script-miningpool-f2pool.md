---
panelgroup: Mining Panels
name: F2 Pool
title: F2 Pool Script
layout: default
description: A graphed 24 hour summary of earnings and current hash rate for F2 Pool account
imageurl: ../images/miningpool-f2pool.png
---

# F2 Pool

The script prepares an image summarizing recent 24 hour summary for an F2 Pool
account.  The current hashrate is depicted, along with a graph showing the
hashrate over the past 24 hours.  Earnings information for the preceding and
current day are also rendered.  

You must have an F2 Pool account and set the account name in the configuration
file.

![sample image of f2pool recent hashrate](../images/miningpool-f2pool.png)

## Script Location

The script is installed at
[~/nodeyez/scripts/miningpool-f2pool.py](../scripts/miningpool-f2pool.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/miningpool-f2pool.json` file

Fields are defined below
  
| field name | description |
| --- | --- |
| accountName | Your account name on f2pool. **required** |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| dataValueColor | The color of the text values for major categories expressed as a Hexadecimal color specifier. Default `#4040ff` | 
| graphLineDarkColor | The color to use for the right and top borders of the blot graph, expressed as a Hexadecimal color specifier. Default `#606060` |
| graphLineLightColor | The color to use for the left and bottom borders of the plot graph, expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
| hashrateNormalDotFillColor | The color to plot a dot for the hashrate when normal at a point in time expressed as a Hexadecimal color specifier. Default `#4040ff`| 
| hashrateNormalDotOutlineColor | The color to make the outline of plotted dots for normal hashrate expressed as a Hexadecimal color specifier. Default `#0000ff` | 
| hashrateLowDotFillColor | The color to plot a dot for the hashrate when it below the low threshold at a point in time expressed as a Hexadecimal color specifier. Default `#ffff40` |
| hashrateLowDotOutlineColor | The color to make the outline of plotted dots for low hashrate expressed as a Hexadecimal color specifier. Default `#ffff00` |
| hashrateLowThreshold | The hashrate level for which hashing should be considered low. Default `60000000000000` |
| hashrateZeroDotFillColor | The color to plot a dot for the hashrate when it is zero/unreported at a point in time expressed as a Hexadecimal color specifier. Default `#ff4040` |
| hashrateZeroDotOutlineColor | The color to make the outline of plotted dots for zero/unreported hashrate expressed as a Hexadecimal color specifier. Default `#ff0000` | 
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `600` |
| movingAverageColor | The color to use for the moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| useTor | Indicates whether remote calls should use tor socks proxy for privacy. Default `true` |
| width | The width, in pixels, to generate the image. Default `480` |

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
python miningpool-f2pool.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-miningpool-f2pool.service

sudo systemctl start nodeyez-miningpool-f2pool.service
```

---

[Home](../) | 