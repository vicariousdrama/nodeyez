---
panelgroup: Other Fun Panels
name: Fiat Price
title: Fiat Price Script
layout: default
description: Shows the current fiat valuation of Bitcoin in US Dollar terms from Bisq marketplace
imageurl: ../images/fiatprice.png
---

# Fiat Price

This script calls upon the bisq marketplace to get the current fiat valuation of
Bitcoin in US Dollar terms and then displays it graphically in large text

![sample price of bitcoin display](../images/fiatprice.png)

## Script Location

The script is installed at
[../scripts/fiatprice.py](../scripts/fiatprice.py).

## Configuration

To configure this script override the default configuration as follows

```shell
nano ../config/fiatprice.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/fiatprice.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| priceurl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
| useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
| showBigText | Indicates whether the current price should be displayed in large mode in the middle instead of at bottom of image. Default `true` |
| showBigTextOnTop | If showBigText is enabled, this controls whether the price rendered below the visual graph or above it in z-order. Default `true` |
| colorBisq | The color to use for the Bisq label expressed as a Hexadecimal color specifier. Default `#40FF40` |
| colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| colorPriceUp | The color of the text for the current price when rising expressed as a Hexadecimal color specifier. Default `#40ff40ff` |
| colorPriceDown | The color of the text for the current price when declining expressed as a Hexadecimal color specifier. Default `#ff4040ff` |
| colorPriceShadow | The color of the text shadow for the current price expressed as a Hexadecimal color specifier. Default `#ffffff7f` |

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

To run this script

Ensure the virtual environment is activated

```shell
source ~/.pyenv/nodeyez/bin/activate
```

And then run it

```shell
cd ~/nodeyez/scripts

python fiatprice.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-fiatprice.service

sudo systemctl start nodeyez-fiatprice.service
```

---

[Home](../) | 
