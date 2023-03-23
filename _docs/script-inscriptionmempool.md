---
panelgroup: Bitcoin Panels
name: Unmined Inscriptions Mempool
title: Unmined Inscriptions Mempool Script
layout: default
description: Shows thumbnail representations of the most recently added inscriptions to the mempool which are not yet mined.
imageurl: ../images/inscriptionmempool.png
---

# Unmined Inscriptions in Mempool

This script calls your local bitcoin node and will analyze your view of the mempool to
identify and extract inscriptions found in transactions.  A summary image of the most
recent inscriptions will be generated as the output file.

- For more information about Ordinals, checkout the [Ordinals Website](https://docs.ordinals.com/).
- For more information about Inscriptions, checkout the [Inscriptions section](https://docs.ordinals.com/inscriptions.html).
- For more technical explanation of OP codes used by this script for parsing out the Ordinal Inscriptions, see the [Script Wiki Page](https://en.bitcoin.it/wiki/Script)

![sample inscription mempool](../images/inscriptionmempool.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/inscriptionmempool.py](../scripts/inscriptionmempool.py)

## Configuration

To configure this script, edit the `~/nodeyez/config/inscriptionmempool.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/inscriptionmempool.png` |
| dataDirectory | The path to store extracted files. A subfolder for ordinals will be created if it doesnt exist. Default `../data/` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `10` |
| colorTextFG | The color to use for the header expressed as a hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |

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
python inscriptionmempool.py
```

Press CTRL+C to stop the process

This script also supports optional command line arguments for a single run and exit.

1. Pass the desired width and height as arguments as follows

```shell
python inscriptionmempool.py 1920 1080
```

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-inscriptionmempool.service

sudo systemctl start nodeyez-inscriptionmempool.service
```

---

[Home](../) | 