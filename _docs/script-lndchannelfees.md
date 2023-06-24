---
panelgroup: Lightning Panels
name: LND Channel Fees
title: Channel Fees script
layout: default
description: Summary report of ratio of value sent and received in channel, fees paid and earned through channels
imageurl: ../images/lndchannelfees.png
---

# LND Channel Fees

This script prepares an image depicting your node's lightning channel routing
velocity and earned fees.  This is initially a basic table listing and will
likely evolve in the future.  Multiple images may be created depending on the
number of open channels.  

Multiple lightning nodes may be reported on. These need to be defined as profiles
available to Nodeyez.  To define profiles you'll need the address, the rest port,
and hex of the macaroon file for that node.  The permissions needed in the macaroon
are

- uri:/lnrpc.Lightning/GetInfo
- uri:/lnrpc.Lightning/GetNodeInfo
- uri:/lnrpc.Lightning/ListChannels
- uri:/lnrpc.Lightning/ChannelBalance
- uri:/lnrpc.Lightning/ForwardingHistory
- uri:/lnrpc.Lightning/ListPayments

The following command can be used to convert a macaroon into the necessary hex
format: `xxd -ps -u -c 1000 nodeyez.macaroon`

![sample image of channel fees](../images/lndchannelfees.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/lndchannelfees.py](../scripts/lndchannelfees.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/lndchannelfees.json` file

Fields are defined below

| field name | description |
| --- | --- |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| dataRowEvenBackgroundColor | The primary color to use as the background for data rows expressed as a Hexadecimal color specifier. Default `#404040` |
| dataRowEvenTextColor | The color of the text for data rows on primary color background expressed as a Hexadecimal color specifier. Default `#ffffff` |
| dataRowOddBackgroundColor | The alternate color to use as the background for data rows expressed as a Hexadecimal color specifier. Default `#202020` |
| dataRowOddTextColor | The color of the text for data rows on alternate color background expressed as a Hexadecimal color specifier. Default `#ffffff` |
| headerText | The text to use in the header area. Default `Channel Usage, Fees and Earnings` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `1800` |
| nodes | An array collection of defined nodes to have channel balances reported via rest calls. |
| nodeDeadColor | The color of the text for a node that has been offline for 1008 blocks expressed as a Hexadecimal color specifier. Default `#ff0000` |
| nodeOfflineColor | The color of the text for an offline node expressed as a Hexadecimal color specifier. Default `#ffa500` |
| pageSize | The number of channels to represent per page rendered. Default `8` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| width | The width, in pixels, to generate the image. Default `480` |

###__nodes__

| field name | description |
| --- | --- |
| enabled | Indicates whether this node definition is enabled for reporting. If set to false, it will be skipped. |
| profileName | The name of the profile for this node. These values should first be defined using the nodeyez-config tool, which saves the profiles to lnd-rest.json |
| headerText | Override the text to use in the header area. |


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
python lndchannelfees.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-lndchannelfees.service

sudo systemctl start nodeyez-lndchannelfees.service
```

---

[Home](../) | 