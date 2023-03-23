---
panelgroup: Mining Panels
name: F2 Pool
title: F2 Pool
layout: default
description: A graphed 24 hour summary of earnings and current hash rate for F2 Pool account
imageurl: ../images/f2pool.png
---

# F2 Pool

The script prepares an image summarizing recent 24 hour summary for an F2 Pool
account.  The current hashrate is depicted, along with a graph showing the
hashrate over the past 24 hours.  Earnings information for the preceding and
current day are also rendered.  

You must have an F2 Pool account and set the account name in the configuration
file.

![sample image of f2pool recent hashrate](../images/f2pool.png)

## Script Location

The script is installed at
[../scripts/f2pool.py](../scripts/f2pool.py).

## Configuration

To configure this script override the default configuration as follows

```sh
nano ../config/f2pool.json
```
  
You should set the following at a minimum
- account
- hashrateLowThreshold: recommend setting this to 10% below your expected hashrate.


| field name | description |
| --- | --- |
| account | Your account name on f2pool. **required** |
| useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
| outputFile | The path to save the generated image. Default `../imageoutput/f2pool.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| hashrateLowThreshold | The hashrate level for which hashing should be considered low. Default `60000000000000` |
| colorDataValue | The color of the text values for major categories expressed as a Hexadecimal color specifier. Default `#4040ff` | 
| colorHashDotFill | The color to plot a dot for the hashrate when normal at a point in time expressed as a Hexadecimal color specifier. Default `#4040ff`| 
| colorHashDotFillZero | The color to plot a dot for the hashrate when it is zero/unreported at a point in time expressed as a Hexadecimal color specifier. Default `#ff4040` |
| colorHashDotFillLow | The color to plot a dot for the hashrate when it below the low threshold at a point in time expressed as a Hexadecimal color specifier. Default `#ffff40` |
| colorHashDotOutline | The color to make the outline of plotted dots for normal hashrate expressed as a Hexadecimal color specifier. Default `#0000ff` | 
| colorHashDotOutlineZero | The color to make the outline of plotted dots for zero/unreported hashrate expressed as a Hexadecimal color specifier. Default `#ff0000` | 
| colorHashDotOutlineLow | The color to make the outline of plotted dots for low hashrate expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorMovingAverage | The color to use for the moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorGraphLineLight | The color to use for the left and bottom borders of the plot graph, expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
| colorGraphLineDark | The color to use for the right and top borders of the blot graph, expressed as a Hexadecimal color specifier. Default `#606060` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `600` |

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

To run this script

Ensure the virtual environment is activated

```shell
source ~/.pyenv/nodeyez/bin/activate
```

And then run it

```shell
cd ~/nodeyez/scripts

python f2pool.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-f2pool.service

sudo systemctl start nodeyez-f2pool.service
```

---

[Home](../) | 

