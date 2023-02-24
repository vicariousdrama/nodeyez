---
panelgroup: Other Fun Panels
name: Compass Mining Status
title: Compass Mining Status Script
layout: default
---

# Compass Mining Status

This script cretaes an image denoting the high level status of facilities with
Compass Mining as reported on their [status page](https://status.compassmining.io)

![sample image of compass mining status](../images/compassminingstatus.png)

## Script Location

The script is installed at 
[/home/nodeyez/nodeyez/scripts/compassminingstatus.py](../scripts/compassminingstatus.py).

## Dependencies

Before running this script you must have met dependencies

- beautifulsoup4 is required for compass mining scripts to parse HTML

```shell
python3 -m pip install beautifulsoup4
```

## Configuration

To configure this script override the default configuration as follows

```shell
nano /home/nodeyez/nodeyez/config/compassminingstatus.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/compassminingstatus.png` |
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

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

To run this script

```shell
cd /home/nodeyez/nodeyez/scripts
/usr/bin/env python3 compassminingstatus.py
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

