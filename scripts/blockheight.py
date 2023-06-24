#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw
from vicariouspanel import NodeyezPanel
import sys
import vicariousbitcoin
import vicarioustext

class BlockHeightPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Block Height panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "textShadowColor": "textShadowColor",
            "textShadowPercent": "textShadowPercent",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerEnabled", False)
        self._defaultattr("interval", 300)
        self._defaultattr("textShadowColor", "#f2a90020")
        self._defaultattr("textShadowPercent", 10)

        # Initialize
        super().__init__(name="blockheight")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blocknumber = vicariousbitcoin.getcurrentblock()

    def run(self):

        super().startImage()

        # Background effects based on block height
        if self.blocknumber % 210000 == 0:
            # last block of halving
            pass
        elif self.blocknumber % 210000 == 1:
            # first block of halving
            pass
        elif self.blocknumber % 210000 == 145782:
            # 69.420% through the halving cycle
            pass
        elif self.blocknumber % 2016 == 0:
            # last block of difficulty period
            pass
        elif self.blocknumber % 2016 == 1:
            # first block of difficulty period
            pass
        elif self.blocknumber % 2100 == 0:
            # whole percentage towards halving
            pass

        # Block height drawn as an alpha layer on top
        blocklayer = Image.new(mode="RGBA", size=(self.canvas.width, self.canvas.height), color=(0,0,0,0))
        blockdraw = ImageDraw.Draw(blocklayer)
        maxFontSize = 128
        minFontSize = 8
        sizeFound = False
        blocknumbertext = f" {self.blocknumber} "
        fs, sw, sh = vicarioustext.getmaxfontsize(self.draw, blocknumbertext, self.width, self.height, True, maxFontSize, minFontSize)
        textFits = fs >= minFontSize
        textShadowSize = ((self.textShadowPercent * fs) // 100)
        textShadowSize = 1 if textShadowSize < 1 else textShadowSize
        textShadowAlphaStart = int(self.textShadowColor[-2:],16)
        textShadowAlphaPerStep = (255 - textShadowAlphaStart) // textShadowSize
        # shadowing
        for shadowStep in range(textShadowSize, 1, -1):
            textShadowAlpha = textShadowAlphaStart + ((1 + textShadowSize - shadowStep) * textShadowAlphaPerStep)
            #print(f"textShadowAlphaPerStep: {textShadowAlphaPerStep}, textShadowSize: {textShadowSize}, shadowStep: {shadowStep}, textShadowAlpha: {textShadowAlpha}")
            shadowColor = ImageColor.getrgb(self.textShadowColor[0:7] + hex(textShadowAlpha)[-2:])
            if textFits:
                vicarioustext.drawcenteredtext(draw=blockdraw, s=blocknumbertext, fontsize=fs, x=(self.width//2) + shadowStep, y=(self.height//2) + shadowStep, textcolor=shadowColor, isbold=True)
            else:
                vicarioustext.drawlefttext(draw=blockdraw, s=blocknumbertext, fontsize=fs, x=0 + shadowStep, y=(self.height//2) + shadowStep, textcolor=shadowColor, isbold=True)
        # normal text
        if textFits:
            vicarioustext.drawcenteredtext(draw=blockdraw, s=blocknumbertext, fontsize=fs, x=(self.width//2), y=(self.height//2), textcolor=ImageColor.getrgb(self.textColor), isbold=True)
        else:
            vicarioustext.drawlefttext(draw=blockdraw, s=blocknumbertext, fontsize=fs, x=0, y=(self.height//2), textcolor=ImageColor.getrgb(self.textColor), isbold=True)
        self.canvas.alpha_composite(blocklayer)
        blocklayer.close()

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates an image based on the blockheight")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configured defaults")
        exit(0)

    # Continuous run
    p = BlockHeightPanel()
    p.runContinuous()