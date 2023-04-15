---
panelgroup: Mining Panels
name: Braiins Pool
title: Braiins Pool Script
layout: default
description: Creates a graph of earnings over the past 30 days of participation in Braiins pool
imageurl: ../images/miningpool-braiinspool.png
---

# Braiins Mining Pool

This script is useful if you have a Braiins (previously known as Slushpool)
mining pool account. To use it, you'll want to add a profile for monitoring
with read access. You can do that on the [Access Profiles page](https://pool.braiins.com/settings/access/). 
The Limited read-only permission is sufficient for the API calls made.

![sample image of braiins pool](../images/miningpool-braiinspool.png)

The pricing and profitability estimates are based on a steady load with no
variance in hashrate and does not take into account change in market price
over time or difficulty adjustments.  This feature will likely be removed
from this panel in future updates.

## Script Location

This script is installed at
[~/nodeyez/scripts/miningpool-braiinspool.py](../scripts/miningpool-braiinspool.py)

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/miningpool-braiinspool.json` file

Fields are defined below

You must set the authtoken field with your API access token

| field name | description |
| --- | --- |
| authtoken | Create your API access  token at https://pool.braiins.com/settings/access/ with limited read-only access, and not web access |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| breakEvenGoodColor | The color of the text showing the break even amount when it is met expressed as a Hexadecimal color specifier. Default `#00ff00` |
| breakEvenMissColor | The color of the text showing the break even amount when it is not met expressed as a Hexadecimal color specifier. Default `#ff0000` |
| dataValueColor | The color of the data field values expressed as a Hexadecimal color specifier. Default `#4040ff` |
| fiatUnit | The three letter fiat currency unit for value comparisons. Supported values are: ARS, AUD, BRL, GBP, CAD, CLP, CNY, CZK, DKK, EUR, HKD, HUF, INR, JPY, MXN, NZD, NGN, NOK, PHP, PLN, RON, RUB, SGD, SEK, CHF, USD, VUV. Default `USD` |
| graphLineDarkColor | The color to draw the top and right and background dashed lines of the graph outline expressed as a Hexadecimal color specifier. Default `#606060` |
| graphLineLightColor | The color to draw the left and bottom of the graph outline expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
| headerColor | The color to use for the image header text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `600` |
| kwhPrice | The price per killowatt you pay for electricity to run the miner. Default `0.12` |
| kwhUsed | The amount of energy used by the miner to run per hour expressed as killowatt hours. Default `1.100` |
| miningBOSRewardColor | The color to draw the bar for the Braiins OS reward expressed as a Hexadecimal color specifier. Default `fb82a8` |
| miningReferralRewardColor | The color to draw the bar for any Referral rewards expressed as a Hexadecimal color specifier. Default `#00bac5` |
| miningRewardColor | The color to draw the bar for the mining reward expressed as a Hexadecimal color specifier. Default `#6b50ff` |
| movingAverageColor | The color of the 14 day moving average line overlaying daily graph bars expressed as a Hexadecimal color specifier. Default `#d69f06` |
| priceCheckInterval | The amount of time, in seconds, the script should wait before checking the price again to use for profitability. 10800 is 3 hours. Default `10800` |
| priceUrl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
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
python miningpool-braiinspool.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-miningpool-braiinspool.service

sudo systemctl start nodeyez-miningpool-braiinspool.service
```

---

[Home](../) | 