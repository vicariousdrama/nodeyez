---
title: System Information Panel
layout: default
---

# System Information

A useful script that reports the CPU temperature and load, drive space in use 
and free, as well as memory usage.  Color coding follows green/yellow/red for
ranging from all OK to heavy usage to warning.

![sample system info panel](../images/sysinfo.png)

This script assumes you are using a Raspberry Pi setup using a MicroSD card for
the OS (/dev/root), and external storage (/dev/sda1) for data files for Bitcoin,
LND, etc.

## Script Location

This script is installed at
[/home/nodeyez/nodeyez/scripts/sysinfo.py](../scripts/sysinfo.py)


## Configuration

To configure this script override the default configuration as follows

```sh
nano /home/nodeyez/nodeyez/config/sysinfo.json
```

| field name | description |
| --- | --- |
| outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/sysinfo.png` |
| colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
| width | The width, in pixels, to generate the image. Default `480` |
| height | The height, in pixels, to generate the image. Default `320` |
| sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
| colorHeader | The color of the header text expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorThermometerUnfilled | The color for the unfilled portion of the thermometer expressed as a Hexadecimal color specifier. Default `#000000` |
| colorThermometerOutline | The color to outline the thermometer expressed as a Hexadecimal color specifier. Default `#c0c0c0` |
| colorThermometerBar | The color to fill the thermometer when normal range expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorThermometerBarWarn | The color to fill the thermometer when warn range expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorThermometerBarHot | The color to fill the thermometer when exceeding hot range expressed as a Hexadecimal color specifier. Default `#ff0000` |
| colorPieOutline | The color to outline the pie charts used for disk space expressed as a Hexadecimal color specifier. Default `#c0c0c0` |
| colorPieEmpty | The color to fill the area of the pie chart for free disk space expressed as a Hexadecimal color specifier. Default `#000000` |
| colorPieEmptyText | The color for labels in the pie chart for free disk space expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorPieGood | The color to fill the area of the pie chart for used disk space expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorPieGoodText | The color for labels in the pie chart for used disk space expressed as a Hexadecimal color specifier. Default `#000000` |
| colorPieWarn | The color to fill the area of the pie chart for used disk space when in warning status expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorPieWarnText | The color for the labels in the pie chart for used disk space when in warning status expressed as a Hexadecimal color specifier. Default `#000000` |
| colorPieDanger | The color to fill the area of the pie chart for used disk space when in danger status expressed as a Hexadecimal color specifier. Default `#ff0000` |
| colorPieDangerText | The color for labels in the pie chart for used disk space when in danger status expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorPieLabelText | The color for the title label of the pie chart for disk space expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorCPUOutline | The color to outline the CPU meters expressed as a Hexadecimal color specifier. Default `#c0c0c0` |
| colorCPUEmpty | The color to fill in CPU meters for unused processing load expressed as a Hexadecimal color specifier. Default `#000000` |
| colorCPUGood | The color to fill in CPU meters for normal processing load expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorCPUWarn | The color to fill in CPU meters for warn levels of processing load expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorCPUDanger | The color to fill in CPU meters for danger levels of processing load expressed as a Hexadecimal color specifier. Default `#ff0000` |
| colorCPULabelText | The color of the labels for the CPU meters expressed as a Hexadecimal color specifier. Default `#ffffff` |
| colorMEMOutline | The color to outline the memory arc display expressed as a Hexadecimal color specifier. Default `#c0c0c0` |
| colorMEMEmpty | The color to fill the memory arc for unused/free memory expressed as a Hexadecimal color specifier. Default `#000000` |
| colorMEMGood | The color to fill the memory arc for used memory in the normal range expressed as a Hexadecimal color specifier. Default `#40ff40` |
| colorMEMWarn | The color to fill the memory arc for used memory in the warning range expressed as a Hexadecimal color specifier. Default `#ffff00` |
| colorMEMDanger | The color to fill the memory arc for used memory when in the danger rnage expressed as a Hexadecimal color specifier. Default `#ff0000` |
| colorMEMLabelText | The color of the labels for the memory arc displays expressed as a Hexadecimal color specifier. Default `#ffffff` |

After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.

## Run Directly

* To run this script

```shell
cd /home/nodeyez/nodeyez/scripts
/usr/bin/env python3 sysinfo.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-sysinfo.service
sudo systemctl start nodeyez-sysinfo.service


---

[Home](../) | 

