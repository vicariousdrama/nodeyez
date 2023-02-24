---
title: NODEYEZ Block Height script
layout: default
---

# Block Height

This script prepares an image displaying the block height.  
It depends on a bitcoin node running locally and fully synched.

![sample image depicting the blockheight reads 693131](../images/blockheight.png)

## Script Location

The script is installed at 
[/home/nodeyez/nodeyez/scripts/blockheight.py](../scripts/blockheight.py).

## Configuration

To configure this script override the default configuration as follows

```shell
nano /home/nodeyez/nodeyez/config/blockheight.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/blockheight.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `120` |

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Running Directly

To run this script

```shell
cd /home/nodeyez/nodeyez/scripts
/usr/bin/env python3 blockheight.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-blockheight.service
sudo systemctl start nodeyez-blockheight.service
```


---

[Home](../) | 

