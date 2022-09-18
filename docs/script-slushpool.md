# ![Nodeyez](../../../raw/branch/main/images/nodeyez.svg)
Display panels to get the most from your node

## Slushpool Mining Pool

This script is useful if you have a Slushpool mining pool account. To use it,
you'll want to add a profile for monitoring with read access. You can do that
on the [Access Profiles page](https://slushpool.com/settings/access/). The 
Limited read-only permission is sufficient for the API calls made.

![sample image of slushpool](../images/slushpool.png)

The pricing and profitability estimates are based on a steady load with no
variance in hashrate and does not take into account change in market price
over time or difficulty adjustments.  This feature will likely be removed
from this panel in future updates.

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/slushpool.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/slushpool.json
   ```

   You must set the authtoken field with your API access token

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/slushpool.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `600` |
   | authtoken | Create your API access  token at https://slushpool.com/settings/access/ with limited read-only access, and not web access |
   | useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `true` |
   | priceurl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
   | priceCheckInterval | The amount of time, in seconds, the script should wait before checking the price again to use for profitability. 10800 is 3 hours. Default `10800` |
   | kwhPrice | The price per killowatt you pay for electricity to run the miner. Default `0.12` |
   | kwhUsed | The amount of energy used by the miner to run per hour expressed as killowatt hours. Default `1.100` |
   | colorHeader | The color to use for the image header text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorMiningReward | The color to draw the bar for the mining reward expressed as a Hexadecimal color specifier. Default `#6b50ff` |
   | colorBOSReward | The color to draw the bar for the Braiins OS reward expressed as a Hexadecimal color specifier. Default `fb82a8` |
   | colorReferralReward | The color to draw the bar for any Referral rewards expressed as a Hexadecimal color specifier. Default `#00bac5` |
   | colorGraphLineLight | The color to draw the left and bottom of the graph outline expressed as a Hexadecimal color specifier. Default `#a0a0a0` |
   | colorGraphLineDark | The color to draw the top and right and background dashed lines of the graph outline expressed as a Hexadecimal color specifier. Default `#606060` |
   | colorMovingAverage | The color of the 14 day moving average line overlaying daily graph bars expressed as a Hexadecimal color specifier. Default `#d69f06` |
   | colorDataValue | The color of the data field values expressed as a Hexadecimal color specifier. Default `#4040ff` |
   | colorBreakEvenMiss | The color of the text showing the break even amount when it is not met expressed as a Hexadecimal color specifier. Default `#ff0000` |
   | colorBreakEvenGood | The color of the text showing the break even amount when it is met expressed as a Hexadecimal color specifier. Default `#00ff00` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

