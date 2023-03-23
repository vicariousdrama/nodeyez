---
panelgroup: Bitcoin Panels
name: OP_RETURN
title: OP_RETURN Script
layout: default
description: Creates an image showing the text entries added in OP_RETURN
imageurl: ../images/opreturn.png
---

# OP_RETURN

This script calls your local bitcoin node and will look for any OP_RETURN entries
on the current block (or specified block).  If suitable entries are found, an image
will be generated rendering the text values.

![sample op return display](../images/opreturn.png)

## Script Location

The script is installed at
[~/nodeyez/scripts/opreturn.py](../scripts/opreturn.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/opreturn.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/opreturn.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
| colorTextFG | The color to use for the header expressed as a hexadecimal color specifier. Default `#ffffff` |
| colorTextFG1 | The primary color to use for OP_RETURN text expressed as a hexadecimal color specifier. Default `#ff7f00` |
| colorTextFG2 | The alternate color to use for OP_RETURN text expressed as a hexadecimal color specifier. Default `#dddd00` |

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
python opreturn.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-opreturn.service

sudo systemctl start nodeyez-opreturn.service
```

---

[Home](../) | 