# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Miner - Braiins OS

This script is useful if you have one or more Bitcoin miners running the Braiins
OS.  It prepares an image showing the power, temperature, fan and pool info
along with a graph of the hashrate produced overtime with moving average and
warning thresholds.  It was created with an Antminer S9 in mind, and the hope
is to improve for other miners over time.

The script is installed at [/home/nodeyez/nodeyez/scripts/minerbraiins.py](../scripts/minerbraiins.py).

![sample image of miner status](../images/minerbraiins.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   ./minerbraiins.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/minerbraiins.json
   ```

   You must set the address for the miner

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/minerbraiins.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `60` |
   | dataDirectory | The base path for the directory to store hashrate history. Default `/home/nodeyez/nodeyez/data/` |
   | colorHot | The color to show the temperature exceeding the hot threshold expressed as a Hexadecimal color specifier. Default `#ffaa00` |
   | colorDangerous | The color to show the temperature exceeding the dangerous threshold expressed as a Hexadecimal color specifier. Default `#ff0000` | 
   | colorHashrateBox | The color of the border, average line and label backgrounds for the hashrate graph expressed as a Hexadecimal color specifier. Default `#202020` |
   | colorHashratePlot | The color to plot each hashrate value within the hashrate graph expressed as a Hexadecimal color specifier. Default `#2f3fc5` |
   | colorHashrateMA | The color to draw the hashrate moving average line expressed as a Hexadecimal color specifier. Default `#40ff40` |
   | miners | An array of one or more miners. The structure of a miner is defined below |

   __miner__

   | field name | description |
   | --- | --- |
   | minerlabel | A unique label to give this miner. If provided, it is used as the label in the header area of the image |
   | mineraddress | *required* The ip or host address for your miner on your local lan, accessible from the host running the script |
   | expectations | An optional structure defining expectations to monitor for. A setting out of range will cause a warning to be rendered. The structure is defined below |


   __expectations__

   | field name | description |
   | --- | --- |
   | power | An optional structure defining power expectations to monitor for. This structure is defined below |
   | hashrate | An optional structure defining hashrate expectations to monitor for. This structure is defined below |
   | pools | An optional structure defining pool definitions of expected pools to send hashrate to. This structure is defined below |

   __power__

   | field name | description |
   | --- | --- |
   | low | An optional property to define the low end of expected power range, in watts. |
   | high | An optional property to define the high end of expected power range, in watts. |

   __hashrate__

   | field name | description |
   | --- | --- |
   | low | An optional property to define the low end of expected hashrate, in MH/s |

   __pools__

   | field name | description |
   | --- | --- |
   | url | The url for a pool that is expected to be configured |
   | user | The user for a pool that is expected to be configured in username.worker format |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

