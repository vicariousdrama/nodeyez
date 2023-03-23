---
panelgroup: Bitcoin Panels
name: Block Height
title: Block Height for Bitcoin
layout: default
description: Renders an image of the current block height. Simple. Refined.
imageurl: ../images/blockheight.png
---

# Block Height

This script prepares an image displaying the block height.  
It depends on a bitcoin node running locally and fully synched.

![sample image depicting the blockheight reads 693131](../images/blockheight.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/blockheight.py](../scripts/blockheight.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/blockheight.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/blockheight.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `120` |

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
python blockheight.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-blockheight.service

sudo systemctl start nodeyez-blockheight.service
```


---

[Home](../) | 

