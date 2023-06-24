#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw
from vicariouspanel import NodeyezPanel
import sys
import vicariousnetwork
import vicarioustext

class FiatPricePanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Fiat Price panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorBisq": "attributionColor",
            "colorHeader": "headerColor",
            "colorPriceDown": "priceDownColor",
            "colorPriceShadow": "priceShadowColor",
            "colorPriceUp": "priceUpColor",
            "colorTextFG": "textColor",
            "priceurl": "priceUrl",
            "sleepInterval": "interval",
            "showBigText": "bigTextEnabled",
            "showBigTextOnTop": "bigTextOnTopEnabled",
            # panel specific key names
            "attributionColor": "attributionColor",
            "bigTextEnabled": "bigTextEnabled",
            "bigTextOnTopEnabled": "bigTextOnTopEnabled",
            "fiatUnit": "fiatUnit",
            "headerColor": "headerColor",
            "priceDownColor": "priceDownColor",
            "priceShadowColor": "priceShadowColor",
            "priceUpColor": "priceUpColor",
            "priceUrl": "priceUrl",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#40ff40")
        self._defaultattr("bigTextEnabled", True)
        self._defaultattr("bigTextOnTopEnabled", True)
        self._defaultattr("fiatUnit", "USD")
        self._defaultattr("headerColor", "#ffffff")
        self._defaultattr("interval", 300)
        self._defaultattr("priceColor", "#40ff40")
        self._defaultattr("priceDownColor", "#ff4040")
        self._defaultattr("priceHigh", 0)
        self._defaultattr("priceLast", 0)
        self._defaultattr("priceLow", 0)
        self._defaultattr("priceShadowColor", "#ffffff7f")
        self._defaultattr("priceUpColor", "#40ff40")
        self._defaultattr("priceUrl", "https://bisq.markets/bisq/api/markets/ticker")
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="fiatprice")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        priceBefore = self.priceLast
        self.priceLast, self.priceHigh, self.priceLow, fiatkeyname = vicariousnetwork.getpriceinfo(self.useTor, self.priceUrl, self.priceLast, self.priceHigh, self.priceLow, self.fiatUnit)
        self.priceChange = self.priceLast - priceBefore
        if self.priceChange < 0:
            self.priceColor = self.priceDownColor
        if self.priceChange > 0:
            self.priceColor = self.priceUpColor

    def run(self):

        self.headerText = f"{self.fiatUnit} Price of Bitcoin"
        super().startImage()

        alphaLayer = Image.new(mode="RGBA", size=(self.canvas.width, self.canvas.height), color=(0,0,0,0))
        alphaDraw = ImageDraw.Draw(alphaLayer)

        priceText = "$" + str(self.priceLast)
        x = self.width//2
        y = self.height//2
        smallPriceSize = int(self.height * 20/320)
        attributionSize = int(self.height * 14/320)
        if self.bigTextEnabled:
            fs, _, _ = vicarioustext.getmaxfontsize(self.draw, priceText, self.width, self.height)
            vicarioustext.drawcenteredtext((self.draw if self.bigTextOnTopEnabled else alphaDraw), priceText, fs, x, y, ImageColor.getrgb(self.priceShadowColor))
            vicarioustext.drawcenteredtext((self.draw if self.bigTextOnTopEnabled else alphaDraw), priceText, fs, x-2, y-2, ImageColor.getrgb(self.priceColor))
        else:
            vicarioustext.drawcenteredtext(self.draw, f"Price: {priceText}", smallPriceSize, x, y, ImageColor.getrgb(self.priceColor))
        # attribution
        vicarioustext.drawbottomlefttext(self.draw, "Data from bisq", attributionSize, 0, self.height, ImageColor.getrgb(self.attributionColor))

        self.canvas.alpha_composite(alphaLayer)
        alphaLayer.close()

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = FiatPricePanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the market rate of BTC from Bisq and renders the price in dollars")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    