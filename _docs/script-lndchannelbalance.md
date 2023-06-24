---
panelgroup: Lightning Panels
name: LND Channel Balance
title: Channel Balance script
layout: default
description: Summary report of LND channel balances with graphical bars showing relative percentage of channel balance on local or remote
imageurl: ../images/lndchannelbalance.png
---

## LND Channel Balance

This script prepares an image depicting your node's lightning channel balances.
Bar graphs show relative percentage of the channel balance on your end or the
remote. Multiple images may be created depending on the number of open channels.

Multiple lightning nodes may be reported on. These need to be defined as profiles
available to Nodeyez.  To define profiles you'll need the address, the rest port,
and hex of the macaroon file for that node.  The permissions needed in the macaroon
are

- uri:/lnrpc.Lightning/GetInfo
- uri:/lnrpc.Lightning/GetNodeInfo
- uri:/lnrpc.Lightning/ListChannels
- uri:/lnrpc.Lightning/ChannelBalance

The following command can be used to convert a macaroon into the necessary hex
format: `xxd -ps -u -c 1000 nodeyez.macaroon`

![sample image of channel balance](../images/lndchannelbalance.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/lndchannelbalance.py](../scripts/lndchannelbalance.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/lndchannelbalance.json` file

Fields are defined below

| field name | description |
| --- | --- |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| barEmptyColor | The color of the unfilled portion representing the remote balance of the channel expressed as a hexadecimal color specifier. Default `#ffa500` |
| barFilledColor | The color of the filled portion representing the local balance of the channel expressed as a hexadecimal color specifier. Default `#008000` |
| barOutlineColor | The color of the outline for the channel balance bar expressed as a hexadecimal color specifier. Default `#808080` |
| displayBalancesEnabled | Indicates whether local and remote channel balance amounts should be rendered along with proportional bar. Default `true` |
| headerText | The text to use in the header area. Default `Lightning Channel Balances` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `1800` |
| nodes | An array collection of defined nodes to have channel balances reported via rest calls. |
| nodeDeadColor | The color of the text for a node that has been offline for 1008 blocks expressed as a Hexadecimal color specifier. Default `#ff0000` |
| nodeOfflineColor | The color of the text for an offline node expressed as a Hexadecimal color specifier. Default `#ffa500` |
| pageSize | The number of channels to represent per page rendered. Default `8` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| width | The width, in pixels, to generate the image. Default `480` |

### __nodes__

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
python lndchannelbalance.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-lndchannelbalance.service

sudo systemctl start nodeyez-lndchannelbalance.service
```

---

[Home](../) | 