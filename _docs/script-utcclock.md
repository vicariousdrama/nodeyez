---
panelgroup: Informational Panels
name: UTC Clock
title: UTC Clock Script
layout: default
description: Renders the date and time. Simple
imageurl: ../images/utcclock.png
---

# UTC Clock

This script provides a simple rendering of the date and time

![sample image depicting the date and time](../images/utcclock.png)

## Script Location
This script is installed at
[~/nodeyez/scripts/utcclock.py](../scripts/utcclock.py)

## Configuration

To configure this script, edit the `~/nodeyez/config/utcclock.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/utcclock.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#602060` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
| colorTextDayOfWeek | The color to render the day of the week expressed as a Hexadecimal color specifier. Default `#e69138` |
| colorTextDate | The color to render the current date expressed as a Hexadecimal color specifier. Default `#f1c232` |
| colorTextTime | The color to render the current time expressed as a Hexadecimal color specifier. Default `#6aa84f` |

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
python utcclock.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-utcclock.service

sudo systemctl start nodeyez-utcclock.service
```

---

[Home](../) | 