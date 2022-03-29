# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Sats per USD

This script calls upon the bisq marketplace to get the current fiat valuation of
Bitcoin in US Dollar terms, and then calculates the sats per dollar and displays
graphically

![sample sats per usd display](../images/satsperusd.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   ./satsperusd.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/satsperusd.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/satsperusd.png` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |
   | priceurl | The url that provides the pricing information from bisq marketplace. Default `https://bisq.markets/bisq/api/markets/ticker` |
   | useTor | Indicates whether remote calls should use torify for privacy. Experimental. Default `false` |
   | satshape | The shape that each individual sat should be drawn. Supported values are: square, circle. Default `square` |
   | showBigText | Indicates whether the current Sats Per USD value should be displayed in large mode in the middle instead of at bottom of image. Default `true` |
   | showBigTextOnTop | If showBigText is enabled, this controls whether the total value is rendered below the sat graph or above it in z-order. Default `true` |
   | colorBisq | The color to use for the Bisq label expressed as a Hexadecimal color specifier. Default `#40FF40` |
   | colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
   | colorSatShape | The color to render each sat expressed as a Hexadecimal color specifier. Default `#ff7f00` |
   | colorSatAmount | The color of the text for the current sats per dollar expressed as a Hexadecimal color specifier. Default `#4040407f` |
   | colorSatAmountShadow | The color of the text shadow for the current sats per dollar expressed as a Hexadecimal color specifier. Default `#ffffff7f` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

