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
[~/nodeyez/scripts/fiatprice.py](../scripts/fiatprice.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/fiatprice.json` file

Fields are defined below

| field name | description |
| --- | --- |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#40FF40` |
| backgroundcolor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| bigTextEnabled | Indicates whether the current price should be displayed in large mode in the middle instead of at bottom of image. Default `true` |
| bigTextOnTopEnabled | If showBigText is enabled, this controls whether the price rendered below the visual graph or above it in z-order. Default `true` |
| fiatUnit | The three letter fiat currency unit for value comparisons. Supported values are: ARS, AUD, BRL, GBP, CAD, CLP, CNY, CZK, DKK, EUR, HKD, HUF, INR, JPY, MXN, NZD, NGN, NOK, PHP, PLN, RON, RUB, SGD, SEK, CHF, USD, VUV. Default `USD` |
| headerColor | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
| priceDownColor | The color of the text for the current price when declining expressed as a Hexadecimal color specifier. Default `#ff4040ff` |
| priceShadowColor | The color of the text shadow for the current price expressed as a Hexadecimal color specifier. Default `#ffffff7f` |
| priceUpColor | The color of the text for the current price when rising expressed as a Hexadecimal color specifier. Default `#40ff40ff` |
| priceUrl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
| useTor | Indicates whether remote calls should use tor socks proxy for privacy. Default `true` |
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