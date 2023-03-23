---
panelgroup: Lightning Panels
name: Channel Balance
title: Channel Balance script
layout: default
description: Summary report of LND channel balances with graphical bars showing relative percentage of channel balance on local or remote
imageurl: ../images/channelbalance.png
---

## Channel Balance

This script prepares an image depicting your node's lightning channel balances.
Bar graphs show relative percentage of the channel balance on your end or the
remote. Multiple images may be created depending on the number of open channels.
It depends on a lighting node.

![sample image of channel balance](../images/channelbalance.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/channelbalance.py](../scripts/channelbalance.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/channelbalance.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/channelbalance.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorNodeOffline | The color of the text for an offline node expressed as a Hexadecimal color specifier. Default `#ffa500` |
| colorNodeDead | The color of the text for a node that has been offline for 1008 blocks expressed as a Hexadecimal color specifier. Default `#ff0000` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| colorBarOutline | The color of the outline for the channel balance bar expressed as a hexadecimal color specifier. Default `#808080` |
| colorBarFilled | The color of the filled portion representing the local balance of the channel expressed as a hexadecimal color specifier. Default `#008000` |
| colorBarEmpty | The color of the unfilled portion representing the remote balance of the channel expressed as a hexadecimal color specifier. Default `#ffa500` |
| displayBalances | Indicates whether local and remote channel balance amounts should be rendered along with proportional bar. Default `true` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `1800` |
| pageSize | The number of channels to represent per page rendered. Default `8` |
| headerText | The text to use in the header area. Default `Lightning Channel Balances` |
| nodes | An array collection of defined nodes to have channel balances reported via rest calls. If this is not provided, then the RPC calls will be made using local LNCLI utility. |

### __nodes__

| field name | description |
| --- | --- |
| enabled | Inidicates whether this node definition is enabled for reporting. If set to false, it will be skipped. |
| address | The address or hostname for this node. It must be reachable from the server running the script. |
| port | The port for which the target node is listening for REST based calls. This is the port referenced in the restlisten setting in bitcoin.conf. |
| useTor | Indicates whether calls to the target node should be made over tor. For internal addresses, this should be set to false. |
| macaroon | The macaroon to use when communicating with the node in hex format. Requires permissions for uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance. If you were using nodeyez on the target node you may use its nodeyez.macaroon created for that node.<br /> To get the hex value, you may use the command:<br />`xxd -ps -u -c 1000 nodeyez.macaroon` |
| __optional__ | __these fields are optional to override the settings above__ |
| outputFile | Override the path to save the generated image. |
| colorTextFG | Override the color of the text expressed as a Hexadecimal color specifier. |
| colorNodeOffline | Override the color of the text for an offline node expressed as a Hexadecimal color specifier. |
| colorNodeDead | Override the color of the text for a node that has been offline for 1008 blocks expressed as a Hexadecimal color specifier. |
| colorBackground | Override the background color of the image expressed as a hexadecimal color specifier. |
| colorBarOutline | Override the color of the outline for the channel balance bar expressed as a hexadecimal color specifier. |
| colorBarFilled | Override the color of the filled portion representing the local balance of the channel expressed as a hexadecimal color specifier. |
| colorBarEmpty | Override the color of the unfilled portion representing the remote balance of the channel expressed as a hexadecimal color specifier. |
| displayBalances | Indicates whether local and remote channel balance amounts should be rendered along with proportional bar. |
| width | Override the width, in pixels, to generate the image. |
| height | Override the height, in pixels, to generate the image. |
| pageSize | Override the number of channels to represent per page rendered. |
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
python channelbalance.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-channelbalance.service

sudo systemctl start nodeyez-channelbalance.service
```

---

[Home](../) | 