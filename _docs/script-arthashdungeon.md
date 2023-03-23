---
panelgroup: Bitcoin Panels
name: Blockhash Dungeon
title: Blockhash Dungeon
layout: default
description: Generates a maze display remiscent of legacy video games based on the Bitcoin Blockhash. The maze is rendered semi deterministically and features customizable tilesets for the floor and walls and logos.
imageurl: ../images/arthashdungeon.png
---

# Blockhash Dungeon

This script produces a maze reminiscent of legacy videogame systems based on the
Bitcoin Blockhash.  The maze is rendered semi deterministically and features
custom tilesets for the maze floor and walls, and logos of popular entities in
the Bitcoin ecosystem. It depends on a bitcoin node running locally and fully
synched.

![sample image depicting a sample generated maze](../images/arthashdungeon.png)

## Script Location

The script is installed at 
[~/nodeyez/scripts/arthashdungeon.py](../scripts/arthashdungeon.py). 

## Configuration

To configure this script, edit the `~/nodeyez/config/arthashdungeon.json` file

Fields are defined below

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `../imageoutput/arthashdungeon.png` |
| bitcoinLogosFile | The path to a file containing tiles of logos to overlay on the maze with dimensions 32x32 pixels, 16 icons wide. Default `../images/arthash-dungeon-bitcoin-logos.png` |
| bitcoinTilesFile | The path to a file containing tiles with dimensions 32x32 arranged in sets of 8 tiles per theme, two themes wide, and 11 themes high. Default `../images/arthash-dungeon-bitcoin-tiles.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |

## Run Directly

Ensure the virtual environment is activated
```shell
source ~/.pyenv/nodeyez/bin/activate
```

Change to the scripts folder
```shell
cd ~/nodeyez/scripts
```

And run it
```shell
python arthashdungeon.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-arthashdungeon.service

sudo systemctl start nodeyez-arthashdungeon.service
```

---

[Home](../) | 