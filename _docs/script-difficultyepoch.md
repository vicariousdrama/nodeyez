---
panelgroup: Bitcoin Panels
name: Difficulty Epoch
title: Difficulty Epoch Script
layout: default
description: An image of the progress through current difficulty epoch denoting blocks expected (green), ahead of schedule (yellow), or behind schedule (red) with estimate of next increase.
imageurl: ../images/difficultyepoch.png
---

# Difficulty Epoch

This script will prepare an image representing the number of blocks that have
been mined thus far in the current difficulty epoch, and indicate if the pace
is ahead of schedule or behind, with an estimated difficulty adjustment to 
occur when the next epoch begins. Each difficulty epoch consists of 2016 blocks.

It depends on a bitcoin node.

![difficulty epoch image sample showing several blocks mined, and ahead of schedule](../images/difficultyepoch.png)

## Script Location
The script is installed at
[~/nodeyez/scripts/difficultyepoch.py](../scripts/difficultyepoch.py).

## Configuration

To manage and configure this script, use the nodeyez-config tool

```sh
sudo nodeyez-config
```

To manually configure this script, edit the `~/nodeyez/config/difficultyepoch.json` file

Fields are defined below

| field name | description |
| --- | --- |
| aheadColor | The color to fill in the block when ahead of schedule, expressed as a Hexadecimal color specifier. Default `#ffff40` |
| backgroundColor | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| behindColor | The color to draw the grid for a block when its not yet mined and was expected to be, expressed as a Hexadecimal color specifier. Default `#ff0000` |
| gridColor | The base color of the grid representing each block during the difficulty period, expressed as a Hexadecimal color specifier. Default `#404040` |
| height | The height, in pixels, to generate the image. Default `320` |
| interval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `540` |
| minedColor | The color to fill in the block when it has been mined by the time expected, expressed as a Hexadecimal color specifie. Default `#40ff40` |
| saveEachBlockEnabled | Indicates whether the result for each block should be saved as a separate image. Useful as source for animated composites. Default `false` |
| textColor | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
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
python difficultyepoch.py
```

Press CTRL+C to stop the process


## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-difficultyepoch.service

sudo systemctl start nodeyez-difficultyepoch.service
```

---

[Home](../) | 