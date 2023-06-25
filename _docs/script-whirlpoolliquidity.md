---
panelgroup: Other Fun Panels
name: Whirlpool Liquidity
title: Whirlpool Liquidity Status
layout: default
description: Shows the Whirlpool pool status indicating number of premixers and remixers in each pool
imageurl: ../images/whirlpoolliquidity.png
---

# Whirlpool Liquidity

This script calls an API to get the whirlpool pool status indicating the number
of premixers and remixers in each pool and then displays a summary panel of
the information.

![sample whirlpool liquidity display](../images/whirlpoolliquidity.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/whirlpoolliquidity.py](../scripts/whirlpoolliquidity.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/whirlpoolliquidity.json` file

Fields are defined below

| field name | description |
| --- | --- |
| apiKey | If you are using a local dojo and whirlpool cli, you must specify the apiKey for communicating with it.  For MyNodeBTC, you can find this on the info page for Whirlpool as the API Key for Whirlpool GUI. Default `NOT_SET` |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#aa2222` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| confirmedColor | The color of the text label for confirmed inputs expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
| elapsedColor | The color of the text label for elapsed time expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
| headerColor | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |
| poolHeaderColor | The color to use for the individual pool header expressed as a Hexadecimal color specifier. Default `#aa2222` |
| registeredColor | The color of the text label for registered inputs expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
| textColor | The color of all other text labels and values expressed as a Hexadecimal color specifier. Default `#ffffff` |
| useTor | Indicates whether remote calls should use tor for privacy. This should not be used for internal/local addresses such as access to whirlpool cli on same system. Default `true` |
| whirlpoolUrl | The url to use for retrieving pool information from whirlpool instance. If you have a local dojo with whirlpool-cli, you may use that server here.  For example, for MyNodeBTC, you can use `https://127.0.0.1:8899`.  Default is the onion address to the Whirlpool Coordinator |
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
python whirlpoolliquidity.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-whirlpoolliquidity.service

sudo systemctl start nodeyez-whirlpoolliquidity.service
```

---

[Home](../) | 