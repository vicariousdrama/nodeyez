---
panelgroup: Nostr Panels
name: Nostr.Band statistics
title: Nostr.Band statistics
layout: default
description: Renders an image of stats about Nostr based on the data collated by Nostr.Band. Currently this depicts a bar chart showing the total number of Zaps per Day
images:
    - ../images/nostrbandstats-zapsperday.png
---

# Nostr.Band Stats

This script prepares an image displaying stats about the Nostr protocol as gathered by Nostr.Band

![sample image of stats for zaps per day](../images/nostrbandstats-zapsperday.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/nostrbandstats.py](../scripts/nostrbandstats.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/nostrbandstats.json` file

Fields are defined below

| field name | description |
| --- | --- |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#A020A0` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| graphAverageColor | The color to use for the average value line drawn across fee rates. Default `#8888FF` |
| graphBorderColor | The color to use for outlining charts and their labels. Default `#888888` |
| graphDataColors | An array of colors to use for multi valued charts. Default: `#A020A0`, `#0000FF`, `#00FF00`, `#808000`, `#FF0000`, `#00FFFF`, `#800000`, `#808080`, `#008000`, `#800080`, `#FF00FF`, `#008080` |
| headerColor | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `86400` |
| statsUrl | The url that provides the stats about Nostr from Nostr.band. Default `https://stats.nostr.band/stats_api?method=stats&options=` |
| useTor | Indicates whether remote calls should use tor socks proxy for privacy. Default `true` |
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
python nostrbandstats.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-nostrbandstats.service

sudo systemctl start nodeyez-nostrbandstats.service
```

---

[Home](../) | 