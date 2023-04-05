---
panelgroup: Other Fun Panels
name: Sats per USD
title: Sats per USD Script
layout: default
description: Shows the current fiat valuation of Bitcoin in US Dollar terms renders as the number of Satoshis you can acquire per Dollar sold.
imageurl: ../images/satsperusd.png
---

# Sats per USD

This script calls upon the bisq marketplace to get the current fiat valuation of
Bitcoin in US Dollar terms, and then calculates the sats per dollar and displays
graphically

![sample sats per usd display](../images/satsperusd.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/satsperusd.py](../scripts/satsperusd.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/satsperusd.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/satsperusd.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |
| priceurl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
| useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
| satshape | The shape that each individual sat should be drawn. Supported values are: square, circle. Default `square` |
| showBigText | Indicates whether the current Sats Per USD value should be displayed in large mode in the middle instead of at bottom of image. Default `true` |
| showBigTextOnTop | If showBigText is enabled, this controls whether the total value is rendered below the sat graph or above it in z-order. Default `true` |
| colorBisq | The color to use for the Bisq label expressed as a Hexadecimal color specifier. Default `#40FF40` |
| colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| colorSatShape | The color to render each sat expressed as a Hexadecimal color specifier. Default `#ff7f00` |
| colorSatAmount | The color of the text for the current sats per dollar expressed as a Hexadecimal color specifier. Default `#4040407f` |
| colorSatAmountShadow | The color of the text shadow for the current sats per dollar expressed as a Hexadecimal color specifier. Default `#ffffff7f` |

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
python satsperusd.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-satsperusd.service

sudo systemctl start nodeyez-satsperusd.service
```

---

[Home](../) | 