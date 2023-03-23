---
panelgroup: Other Fun Panels
name: Compass Mining Status
title: Compass Mining Status Script
layout: default
description: Prepares an image showin the high level status of facilities that are in Maintenance, Critical, Major issue status
imageurl: ../images/compassminingstatus.png
---

# Compass Mining Status

This script creates an image denoting the high level status of facilities with
Compass Mining as reported on their [status page](https://status.compassmining.io)

![sample image of compass mining status](../images/compassminingstatus.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/compassminingstatus.py](../scripts/compassminingstatus.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/compassminingstatus.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/compassminingstatus.png` |
| statusurl | The url that provides current compass mining facility status. Default `https://status.compassmining.io/` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| colorGoodText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as good. Default `#40ff40` |
| colorMaintenance | The color of the background expressed as a Hexadecimal color specifier when a facility is listed as maintenance. Default `#2020ff` |
| colorMaintenanceText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as maintenance. Default `#ffffff` | 
| colorCritical | The color of the background expressed as a Hexadecimal color specifier when a facility is listed as critical. Default `#ff7a00` | 
| colorCriticalText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as critical. Default `#ffffff` | 
| colorMajor | The color of the background expressed as a Hexadecimal color specifier when a facility is listed as major. Default `#ff2020` |
| colorMajorText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as major. Default `#ffffff` |  
| colorNone | The color of the background expressed as a Hexadecimal color specifier when a facility is listed as none. Default `#333333` | 
| colorNoneText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as none. Default `#ffffff` |
| colorMinor | The color of the background expressed as a Hexadecimal color specifier when a facility is listed as minor. Default `#2020ff` |
| colorMinorText | The color of the text expressed as a Hexadecimal color specifier when a facility is listed as minor. Default `#ffffff` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |

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
python compassminingstatus.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-compassminingstatus.service

sudo systemctl start nodeyez-compassminingstatus.service
```

---

[Home](../) | 