---
panelgroup: Other Fun Panels
name: Fear and Greed Index
title: Fear and Greed Script
layout: default
description: Graphs the Fear and Greed index from alternative.me with a moving average trend over time and indicator of highest value
imageurl: ../images/fearandgreed.png
---

# Fear and Greed Index

This script can use previously retrieved data for the Fear and Greed index as
determined and made available by alternative.me.  A graph of the trend over
time is depicted as well as displaying the current level and descriptor at
the top of the image.

![sample image of fear and greed index](../images/fearandgreed.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/fearandgreed.py](../scripts/fearandgreed.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/fearandgreed.json` file

Fields are defined below

| field name | description |
| --- | --- |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#aa2222` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| dataValueColor | The color of the data values for each entry expressed as a Hexadecimal color specifier. Default `#ff7f00` |
| graphLineDarkColor | The color to draw the top and right and background dashed lines of the graph outline expressed as a Hexadecimal color specifier. Default `#606060` |
| graphLineLightColor | The color to draw the left and bottom of the graph outline expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `43200` |
| movingAverageColor | The color to use for the moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| url | The url that provides the fear and greed information. Default `https://api.alternative.me/fng/?limit=0&format=json&date_format=cn` |
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
python fearandgreed.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-daily-data-retrieval.service

sudo systemctl start nodeyez-daily-data-retrieval.service
```

---

[Home](../) | 