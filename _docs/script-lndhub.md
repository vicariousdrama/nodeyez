---
panelgroup: Lightning Panels
name: LNDHub Account Balances
title: LNDHub Account Balances Script
layout: default
description: Summary of accounts in a local LNDHub instance with reporting of receives and spends, balance, and fees the hub has earned per account
imageurl: ../images/lndhub.png
---

# LND Hub Account Balances

This script is useful if you are operating a local intance of LND Hub to
support your own lightning wallets like BlueWallet connected to your node
or if you are acting as a "bank" for friends and family who dont have their
own node.  

Lightning server implementations generally only provide a per channel 
balance, or the overall wallet balance for the server as they are
unaware of subaccounts.  This can cause challenges if you don't know how
much of the server balance belongs to others vs yourself when using general
tools like Ride the Lightning, Thunderhub, Zeus LN that operate at the
server level.

With this script, you can produce a summary of all accounts in the system,
the total funds they have received and spent through invoices, and their
balance.

Optionally, further metadata for users, such as the date their account was
created, total fees paid to the hub, and number of funding and spending
transactions may also be displayed.

![sample image of lnd hub](../images/lndhub.png)

The script limits output to that which will fit on a single screen, which
should allow for anywhere from about 4 to 8 accounts.  If you need
pagination support for more accounts, please file an issue or contact
me directly.

## Script Location

This script is installed at
[~/nodeyez/scripts/lndhub.py](../scripts/lndhub.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/lndhub.json` file

Fields are defined below

| field name | description |
| --- | --- |
| attributionColor | The text color for the source attribution line expressed as a Hexadecimal color specifier. Default `#80cef2` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| headerText | The text to use in the header area. Default `LNDHub Account Balances` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `600` |
| lineColor | The color of the line dividing the subheader from user records expressed as a Hexadecimal color specifier. Default `#4040ff` |
| logDetailsEnabled | Indicates whether the debug info should be printed out. Default `true` |
| redisDb | The redis database number to load. Default `0` |
| redisPort | The port of the redis server. Default `6379` |
| redisServer | The hostname of the redis server. Default `localhost` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| userDetailsEnabled | Indicates whether user details should be output to the image (create date, hub fees, txs). Default `true` |
| userDetailsTextColor | The color of the account detail text expressed as a Hexadecimal color specifier. Default `#808080` |
| userAccounts | An array of user account definitions associating names to the account id |
| width | The width, in pixels, to generate the image. Default `480` |

__userAccounts__

| field name | description |
| --- | --- |
| accountid | The account identifier. (e.g. 'f9095b00b85802c6ff9cc674231858af03a24a75353aa7c0') |
| email | Optional email associated to account |
| name | The alias given to the account |
| notes | Additional notes about the account |
| phone | Optional phone associated to the account |

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
python lndhub.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-lndhub.service

sudo systemctl start nodeyez-lndhub.service
```

---

[Home](../) | 