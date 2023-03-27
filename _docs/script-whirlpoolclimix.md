---
panelgroup: Other Fun Panels
name: Whirlpool CLI Mix Status
title: Whirlpool CLI Mix Status script
layout: default
description: Depicts the status of your Whirlpool Client for whether its connected and participating in mixes
imageurl: ../images/whirlpoolclimix.png
---

# Whirlpool CLI Mix

This script makes API calls to a whirlpool client you run to get information
about its state, and the mixes you have setup to participate in and then
generates a status panel of this information.

![sample whirlpool liquidity display](../images/whirlpoolclimix.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/whirlpoolclimax.py](../scripts/whirlpoolclimax.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/whirlpoolclimix.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/whirlpoolclimix.png` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| useTor | Indicates whether remote calls should use tor for privacy. This should not be used for internal/local addresses such as access to whirlpool cli on same system. Experimental. Default `false` |
| whirlpoolurl | The base url to use for retrieving whirlpool information.  You should use your local whirlpool cli, not the whirlpool coordinator. Default `https://127.0.0.1:8899` |
| apiKey | You must specify the apiKey for communicating with your local whirlpool instance. |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| colorDataLabel | The color of the text for field labels expressed as a Hexadecimal color specifier. Default `#aa2222` |
| colorDataValue | The color of the text for field values expressed as a Hexadecimal color specifier. Default `#bbbbbb` |
| colorDataOn | The color of the indicator when something is on/true. Default `#40ff40` |
| colorDataOff | The color of the indicator when something is off/false. Default `#ff4040` |
| colorTextFG | The color of all other text labels and values expressed as a Hexadecimal color specifier. Default `#ffffff` |

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
```
python whirlpoolclimix.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-whirlpoolclimix.service

sudo systemctl start nodeyez-whirlpoolclimix.service
```

---

[Home](../) | 