---
title: NODEYEZ Arthash - Geometric artwork based on blockhash
---

# Art Hash

This script produces geometric artwork deterministically based on Bitcoin
Blockhash values. It depends on a bitcoin node running locally and fully
synched.


![sample image depicting hash as colored triangles](../images/arthash-719360.png)

## Script Location

The script is installed at 
[/home/nodeyez/nodeyez/scripts/arthash.py](../scripts/arthash.py). 

## Configuration

To configure this script

Override the default configuration as follows

```sh
nano /home/nodeyez/nodeyez/config/arthash.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/arthash.png` |
| colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorShapeOutline | The color of the outline for shapes expressed as a hexadecimal color specifier. Default `#ffffff` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

To run this script

```shell
cd /home/nodeyez/nodeyez/scripts
/usr/bin/env python3 arthash.py
```

Press CTRL+C to stop the process


## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-arthash.service
sudo systemctl start nodeyez-arthash.service
```

---

[Home](../README.md) | 
