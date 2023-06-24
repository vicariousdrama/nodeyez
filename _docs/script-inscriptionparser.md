---
panelgroup: Bitcoin Panels
name: Inscription Parser
title: Inscription Parser Script
layout: default
description: Parses inscriptions from blocks, creates display wrappers for each with metadata
imageurl: ../images/inscriptionparser.png
---

# Inscription Parser

This script analyzes a block, finds transactions with inscriptions and extracts them. 

It depends on a bitcoin node.

- For more information about Ordinals, checkout the [Ordinals Website](https://docs.ordinals.com/).
- For more information about Inscriptions, checkout the [Inscriptions section](https://docs.ordinals.com/inscriptions.html).
- For more technical explanation of OP codes used by this script for parsing out the Ordinal Inscriptions, see the [Script Wiki Page](https://en.bitcoin.it/wiki/Script)

![sample ordinal display](../images/inscriptionparser.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/inscriptionparser.py](../scripts/inscriptionparser.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/inscriptionparser.json` file

Fields are defined below

| field name | description |
| --- | --- |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| exportFilesEnabled | Indicates whether files should be exported to the data directory. Default `true` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
| overlayBackgroundColor | If overlayEnabled, this is the background color of the overlay block as a Hexadecimal color specifier. Default `#00000040` |
| overlayEnabled | Indicates whether annotations should be labeled over the image to display the transaction id, content type and size information. Default `true` |
| overlayExifEnabled | Indicates whether key exif data found in images should be labeled over the image in the annotation block. Default `true` |
| overlayTextColor | If overlayEnabled, this is the color of the overlay text as a Hexadecimal color specifier. `#ffffffff` |
| textColor | The color to use for the header expressed as a 
hexadecimal color specifier. Default `#ffffff` |
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
python inscriptionparser.py
```

Press CTRL+C to stop the process

This script also supports optional command line arguments for a single run and exit.

1. Pass the desired block number as an argument as follows

```shell
python inscriptionparser.py 773046
```

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-inscriptionparser.service

sudo systemctl start nodeyez-inscriptionparser.service
```

---

[Home](../) | 