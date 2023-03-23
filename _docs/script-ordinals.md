---
panelgroup: Bitcoin Panels
name: Ordinal Inscriptions
title: Ordinal Inscriptions Script
layout: default
description: Parses out ordinal inscriptions from blocks, creates display wrappers for each with metadata
imageurl: ../images/ordinals.png
---

# Ordinal Inscriptions

This script calls your local bitcoin node and will look for any transaction entries
where the input data matches the structure of Ordinal Inscriptions.  It will then 
parse out the data, and for each image will prepare a display image wrapper depicting
the image, the block, and the txid.

- For more information about Ordinals, checkout the [Ordinals Website](https://docs.ordinals.com/).
- For more information about Inscriptions, checkout the [Inscriptions section](https://docs.ordinals.com/inscriptions.html).
- For more technical explanation of OP codes used by this script for parsing out the Ordinal Inscriptions, see the [Script Wiki Page](https://en.bitcoin.it/wiki/Script)

![sample ordinal display](../images/ordinals.png)

## Script Location

This script is installed at
[~/nodeyez/scripts/ordinals.py](../scripts/ordinals.py).

## Configuration

To configure this script, edit the `~/nodeyez/config/ordinals.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/ordinals.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
| colorTextFG | The color to use for the header expressed as a hexadecimal color specifier. Default `#ffffff` |
| dataDirectory | The path to store extracted files. A subfolder for ordinals will be created if it doesnt exist. Default `../data/` |
| exportFilesToDataDirectory | Indicates whether files should be exported to the data directory. Default `true` |
| saveUniqueImageNames | Indicates whether unique image names should be created for each inscription. Default `true` |
| overlayTextEnabled | Indicates whether annotations should be labeled over the image to display the transaction id, content type and size information. Default `true` |
| overlayExifEnabled | Indicates whether key exif data found in images should be labeled over the image in the annotation block. Default `true` |
| overlayTextBG | If overlayTextEnabled is true, this is the color of the annotation text background overlay expressed as a Hexadecimal color specifier. Default `#00000080` |
| overlayTextFG | If overlayTextEnabled is true, this is the color of the annotation text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| uniqueOutputFile | The path to save individual generated images for each inscription. This is a base path where the block number and index of the transaction in the block will be included at the end of the file name but before the extension. Default `../imageoutput/ordinals/ordinals.png` |
| blocklistURL | An optional URL to a resource that provides a list of block inscriptions not to extract. Default `https://nodeyez.com/sample-config/ordblocklist.json` |
| useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |

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
python ordinals.py
```

Press CTRL+C to stop the process

This script also supports optional command line arguments for a single run and exit.

1. Pass the desired block number or range as an argument as follows

```shell
python ordinals.py 773046
# or
python ordinals.py 775000-775100
```

2. Pass the desired block number or range, width and height as arguments

```shell
python ordinals.py 774411 800 600
# or
python ordinals.py 775123-775223 1920 1080
```

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-ordinals.service

sudo systemctl start nodeyez-ordinals.service
```

---

[Home](../) | 