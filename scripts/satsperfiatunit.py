#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousnetwork
import vicarioustext

class SatsPerFiatUnitPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Sats per Fiat Unit panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorBisq": "attributionColor",
            "colorHeader": "headerColor",
            "colorSatAmount": "priceUpColor",
            "colorSatAmountShadow": "priceShadowColor",
            "colorSatShape": "satShapeColor",
            "colorTextFG": "textColor",
            "priceurl": "priceUrl",
            "satshape": "satShape",
            "showBigText": "bigTextEnabled",
            "showBigTextOnTop": "bigTextOnTopEnabled",
            "sleepInterval": "interval",
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
            "satShape": "satShape",
            "satShapeColor": "satShapeColor",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#1bd8f4")
        self._defaultattr("bigTextEnabled", True)
        self._defaultattr("bigTextOnTopEnabled", True)
        self._defaultattr("fiatUnit", "USD")
        self._defaultattr("headerColor", "#ffffff")
        self._defaultattr("interval", 300)
        self._defaultattr("priceColor", "#40ff40")
        self._defaultattr("priceDownColor", "#ff40407f")
        self._defaultattr("priceHigh", 0)
        self._defaultattr("priceLast", 0)
        self._defaultattr("priceLow", 0)
        self._defaultattr("priceShadowColor", "#ffffff7f")
        self._defaultattr("priceUpColor", "#40ff407f")
        self._defaultattr("priceUrl", "https://mempool.space/api/v1/prices")
        self._defaultattr("satShape", "square") # circle, square, symbol-s, triangle
        self._defaultattr("satShapeColor", "#ff7f00")
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "topleft")

        # Initialize
        super().__init__(name="satsperfiatunit")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        priceBefore = self.priceLast
        self.priceLast, self.priceHigh, self.priceLow, fiatkeyname = vicariousnetwork.getpriceinfo(self.useTor, self.priceUrl, self.priceLast, self.priceHigh, self.priceLow, self.fiatUnit)
        self.priceChange = self.priceLast - priceBefore
        if self.priceChange < 0:
            self.priceColor = self.priceDownColor
        if self.priceChange > 0:
            self.priceColor = self.priceUpColor
        if fiatkeyname != f"{self.fiatUnit}".upper():
            self.fiatUnit = fiatkeyname.upper()

    def getSatsPerFiatUnit(self):
        return int(round(100000000.0 / self.priceLast))

    def renderAttribution(self):
        fontsize = int(self.height * 16/320)
        vicarioustext.drawbottomlefttext(self.draw, "Data from mempool", fontsize, 0, self.height, ImageColor.getrgb(self.attributionColor))

    def renderBigTextOver(self):
        if not self.bigTextEnabled: return
        if not self.bigTextOnTopEnabled: return
        fontsize = int(self.height * 128/320)
        t = str(self.getSatsPerFiatUnit())
        cx = self.width//2
        cy = self.getInsetTop() + (self.getInsetHeight() // 2)
        overlay = Image.new(mode="RGBA", size=(self.width,self.height), color=(0,0,0,0))
        draw = ImageDraw.Draw(overlay)
        vicarioustext.drawcenteredtext(draw, t, fontsize, cx, cy, ImageColor.getrgb(self.priceShadowColor))
        vicarioustext.drawcenteredtext(draw, t, fontsize, cx-2, cy-2, ImageColor.getrgb(self.priceColor))
        self.canvas.alpha_composite(overlay)
        overlay.close()

    def renderBigTextUnder(self):
        if not self.bigTextEnabled: return
        if self.bigTextOnTopEnabled: return
        fontsize = int(self.height * 128/320)
        t = str(self.getSatsPerFiatUnit())
        cx = self.width//2
        cy = self.getInsetTop() + (self.getInsetHeight() // 2)
        vicarioustext.drawcenteredtext(self.draw, t, fontsize, cx, cy, ImageColor.getrgb(self.priceShadowColor))
        vicarioustext.drawcenteredtext(self.draw, t, fontsize, cx-2, cy-2, ImageColor.getrgb(self.priceColor))

    def renderGrid(self):
        col = 0
        row = 0
        while self.satsRemaining > 100:
            self.satsRemaining -= 100
            self.renderGridSquare(col,row,100)
            col += 1
            if col >= self.satGridCols:
                row += 1
                col = 0
        self.renderGridSquare(col,row,self.satsRemaining)

    def renderGridSquare(self, col, row, satsleft):
        fillColor = ImageColor.getrgb(self.satShapeColor)
        for y in range(10):
            for x in range(10):
                if satsleft > 0:
                    left = (self.satGridLeft + (col*11*self.satSidePixels) + (x*self.satSidePixels))
                    top = (self.satGridTop + (row*11*self.satSidePixels) + (y*self.satSidePixels))
                    right = left + self.satSidePixels - 2
                    bottom = top + self.satSidePixels - 2
                    fontsize = int((bottom - top)) # * .8)
                    fontsize = 1 if fontsize < 1 else fontsize
                    middleh = left + ((right-left)//2)
                    middlev = top + ((bottom-top)//2)
                    if self.satShape == "circle":
                        self.draw.ellipse(xy=((left,top),(right,bottom)),fill=fillColor)
                    elif self.satShape == "square":
                        self.draw.rectangle(xy=((left,top),(right,bottom)),fill=fillColor)
                    elif self.satShape == "symbol-s":
                        t = u'Ⓢ'
                        t = u's'
                        vicarioustext.drawcenteredtext(self.draw, t, fontsize, middleh, middlev, fillColor)
                        self.draw.ellipse(xy=((left+1,top+1),(right-1,bottom-1)),outline=fillColor, width=2)
                    elif self.satShape == "triangle":                            
                        self.draw.polygon(xy=((left,bottom),(middleh,top),(right,bottom)),fill=fillColor)
                    else: # square
                        self.draw.rectangle(xy=((left,top),(right,bottom)),fill=fillColor)
                    satsleft -= 1
                else:
                    return

    def renderPrices(self):
        satsperfiatunit = self.getSatsPerFiatUnit()
        satsperfiatunitlow = int(round(100000000.0 / self.priceLow))
        satsperfiatunithigh = int(round(100000000.0 / self.priceHigh))
        fontsize = int(self.height * 20/320)
        y = self.getInsetTop() + self.getInsetHeight() - fontsize
        if not self.bigTextEnabled:
            t = f"Last: {satsperfiatunit}"
        else:
            t = f"24 hour range: {satsperfiatunithigh} to {satsperfiatunitlow}"
        vicarioustext.drawcenteredtext(self.draw, t, fontsize, self.width//2, y)

    def run(self):
        self.headerText = f"Sats Per {self.fiatUnit}"
        super().startImage()
        self.renderBigTextUnder()
        self.setupSatSizing()
        self.renderGrid()
        self.renderBigTextOver()
        self.renderPrices()
        self.renderAttribution()
        super().finishImage()

    def setupSatSizing(self):
        self.satsRemaining = self.getSatsPerFiatUnit()
        colset = {0:1,50:2,200:3,300:4,400:5,1000:6,1400:7,1800:8,3200:9,
                  4500:10,5000:11,5500:12,8400:13,9100:14,9800:15,15000:21}
        maxk = 0
        maxv = 1
        for k in colset.keys():
            v = colset[k]
            if self.satsRemaining > k: 
                if k > maxk and v > maxv:
                    maxk = k
                    maxv = v
        self.satGridCols = maxv
        self.satsWide = (self.satGridCols * 10) + (self.satGridCols - 1)
        self.satSidePixels = self.width // self.satsWide
        self.satGridLeft = (self.width - (self.satsWide * self.satSidePixels))//2
        self.satGridRows = math.ceil(self.satsRemaining / (maxv * 100))
        self.satsHigh = (self.satGridRows * 10) + (self.satGridRows - 1)
        priceHeightBuffer = int(self.height * 30/320)
        self.satGridTop = self.getInsetTop() + ((self.getInsetHeight() - priceHeightBuffer - (self.satsHigh * self.satSidePixels))//2)
        if self.satGridTop < self.getInsetTop(): self.satGridTop = self.getInsetTop()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = SatsPerFiatUnitPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the market rate of BTC from Bisq and renders number of Sats per Fiat Unit")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()
