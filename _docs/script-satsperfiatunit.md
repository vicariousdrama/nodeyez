---
panelgroup: Other Fun Panels
name: Sats per Fiat Unit
title: Sats per Fiat Unit Script
layout: default
description: Shows the current fiat valuation of Bitcoin rendered as the number of Satoshis you can acquire per fiat unit sold.
imageurl: ../images/satsperfiatunit.png
---

# Sats per Fiat Unit

This script calls upon the bisq marketplace to get the current fiat valuation of
Bitcoin, and then calculates the sats per fiat unit to display graphically.

![sample sats per usd display](../images/satsperfiatunit.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/satsperfiatunit.py](../scripts/satsperfiatunit.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/satsperfiatunit.json` file

Fields are defined below

| field name | description |
| --- | --- |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#40FF40` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| bigTextEnabled | Indicates whether the current Sats Per USD value should be displayed in large mode in the middle instead of at bottom of image. Default `true` |
| bigTextOnTopEnabled | If bigTextEnabled is true, this controls whether the total value is rendered below the sat graph or above it in z-order. Default `true` |
| fiatUnit | The three letter fiat currency unit for value comparisons. Supported values are: ARS, AUD, BRL, GBP, CAD, CLP, CNY, CZK, DKK, EUR, HKD, HUF, INR, JPY, MXN, NZD, NGN, NOK, PHP, PLN, RON, RUB, SGD, SEK, CHF, USD, VUV. Default `USD` |
| headerColor | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |
| priceShadowColor | The color of the text shadow for the current sats per dollar expressed as a Hexadecimal color specifier. Default `#ffffff7f` |
| priceDownColor | The color of the text for the current sats per fiat unit expressed as a Hexadecimal color specifier. Default `#ff40407f` |
| priceUpColor | The color of the text for the current sats per fiat unit expressed as a Hexadecimal color specifier. Default `#40ff407f` |
| priceUrl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
| satshape | The shape that each individual sat should be drawn. Supported values are: circle, square, symbol-s, triangle. Default `square` |
| satShapeColor | The color to render each sat expressed as a Hexadecimal color specifier. Default `#ff7f00` |
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
python satsperfiatunit.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-satsperfiatunit.service

sudo systemctl start nodeyez-satsperfiatunit.service
```

---

[Home](../) | 