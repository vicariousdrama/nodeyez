# ![Nodeyez](../../../../raw/branch/main/images/nodeyez.svg)
Display panels to get the most from your node

## Whirlpool CLI Mix

This script makes API calls to a whirlpool client you run to get information
about its state, and the mixes you have setup to participate in and then
generates a status panel of this information.

![sample whirlpool liquidity display](../images/whirlpoolclimix.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/whirlpoolclimix.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/whirlpoolclimix.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/whirlpoolclimix.png` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |
   | useTor | Indicates whether remote calls should use tor for privacy. This should not be used for internal/local addresses such as access to whirlpool cli on same system. Experimental. Default `false` |
   | whirlpoolurl | The base url to use for retrieving whirlpool information.  You should use your local whirlpool cli, not the whirlpool coordinator. Default `https://127.0.0.1:8899` |
   | apiKey | You must specify the apiKey for communicating with your local whirlpool instance. |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
   | colorDataLabel | The color of the text for field labels expressed as a Hexadecimal color specifier. Default `#aa2222` |
   | colorDataValue | The color of the text for field values expressed as a Hexadecimal color specifier. Default `#bbbbbb` |
   | colorTextFG | The color of all other text labels and values expressed as a Hexadecimal color specifier. Default `#ffffff` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

