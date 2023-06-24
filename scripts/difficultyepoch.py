#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import math
import sys
import time
import vicariousbitcoin
import vicarioustext

class DifficultyEpochPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Difficulty Epoch panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorGrid": "gridColor",
            "colorAhead": "aheadColor",
            "colorBehind": "behindColor",
            "colorMined": "minedColor",
            "colorTextFG": "textColor",
            "saveEachBlock": "saveEachBlockEnabled",
            "sleepInterval": "interval",
            # panel specific key names
            "aheadColor": "aheadColor",
            "behindColor": "behindColor",
            "gridColor": "gridColor",
            "minedColor": "minedColor",
            "saveEachBlockEnabled": "saveEachBlockEnabled"
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("aheadColor", "#ffff40")
        self._defaultattr("behindColor", "#ff0000")
        self._defaultattr("gridColor", "#404040")
        self._defaultattr("headerText", "Blocks Mined This Difficulty Epoch")
        self._defaultattr("interval", 540)
        self._defaultattr("minedColor", "#40ff40")
        self._defaultattr("saveEachBlockEnabled", False)

        # Initialize
        super().__init__(name="difficultyepoch")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blockheight = vicariousbitcoin.getcurrentblock()
        j = vicariousbitcoin.getblock(vicariousbitcoin.getfirstblockforepoch(self.blockheight))
        self.epochBlocksMined = int(j["confirmations"])
        self.epochBeganTime = int(j["time"])

    def _buildEpochDescription(self, s, d, i, l):
        if s > i:
            n = s // i
            d = f"{d}, " if len(d) > 0 else d
            d = f"{d}{n} {l}"
            d = f"{d}s" if n > 1 else d
            s -= (n*i)
        return s, d

    def run(self):

        self.pageSuffix = "" if not self.saveEachBlockEnabled else f"{self.blockheight}"
        super().startImage()

        blocksPerDifficultyEpoch = 2016
        secondsPerBlockExpected = 600

        currentTime = int(time.time())
        secondsPassed = currentTime - self.epochBeganTime
        epochBlocksExpected = 1 if self.epochBlocksMined == 1 else secondsPassed // secondsPerBlockExpected
        nextAdjustment = "0.0"
        if float(epochBlocksExpected) > 0 and float(self.epochBlocksMined) > 0:
            nextAdjustment = str(float("%.2f" % (((float(self.epochBlocksMined) / float(epochBlocksExpected)) - 1.0) * 100)))
        adjustcolor = self.behindColor
        if "-" not in nextAdjustment:
            nextAdjustment = f"+{nextAdjustment}"
            adjustcolor = self.minedColor
        epochEndETA = self.epochBeganTime + (blocksPerDifficultyEpoch * secondsPerBlockExpected)
        if float(self.epochBlocksMined) > 0:
            epochEndETA = int(math.floor((float(secondsPassed) / float(self.epochBlocksMined))*blocksPerDifficultyEpoch)) + self.epochBeganTime
        secondsToEpochEndETA = epochEndETA - currentTime
        nextEpochDescription = ""
        if self.epochBlocksMined >= 10:
            secondsToEpochEndETA, nextEpochDescription = self._buildEpochDescription(secondsToEpochEndETA, nextEpochDescription, 86400, "day")
            secondsToEpochEndETA, nextEpochDescription = self._buildEpochDescription(secondsToEpochEndETA, nextEpochDescription, 3600, "hour")
            if secondsToEpochEndETA > secondsPerBlockExpected and nextEpochDescription.find(",") == -1:
                secondsToEpochEndETA, nextEpochDescription = self._buildEpochDescription(secondsToEpochEndETA, nextEpochDescription, 60, "minute")
            elif len(nextEpochDescription) == 0:
                nextEpochDescription = "a few minutes"
        else:
            nextEpochDescription = "about 2 weeks"

        # grid
        gridRows = 32
        blocksPerGridRow = blocksPerDifficultyEpoch // gridRows # 63
        blockw=int(math.floor(self.width/blocksPerGridRow))
        padleft=int(math.floor((self.width-(blocksPerGridRow*blockw))/2))
        padtop=self.getInsetTop()
        currentminedcolor = self.textColor
        for dc in range(blocksPerGridRow):
            for dr in range(gridRows):
                epochblocknum = ((dr*blocksPerGridRow) + dc)+1
                tlx = (padleft + (dc*blockw))
                tly = (padtop + (dr*blockw))
                brx = tlx+blockw-2
                bry = tly+blockw-2
                if epochblocknum <= self.epochBlocksMined:
                    fillcolor = self.minedColor
                    if epochblocknum > epochBlocksExpected:
                        fillcolor = self.aheadColor
                        currentminedcolor = self.aheadColor
                    self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=ImageColor.getrgb(fillcolor))
                else:
                    outlinecolor = self.gridColor
                    if epochblocknum <= epochBlocksExpected:
                        outlinecolor = self.behindColor
                        currentminedcolor = self.behindColor
                    self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=None,outline=ImageColor.getrgb(outlinecolor))
        # labels
        fs = int(self.height * (18/320))    # 18 default font size for 320 pixel high image
        labelHeight = int(fs * 1.40)
        col1X = int(self.width * .25)
        col2X = int(self.width * .60)
        row1Y = self.getInsetTop() + self.getInsetHeight() - (labelHeight * 2)
        row2Y = self.getInsetTop() + self.getInsetHeight() - (labelHeight * 1)
        vicarioustext.drawtoprighttext(self.draw, "Expected: ",              fs, col1X, row1Y, ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoplefttext(self.draw, f"{epochBlocksExpected}",   fs, col1X, row1Y, ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoprighttext(self.draw, "Mined: ",                 fs, col1X, row2Y, ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoplefttext(self.draw, f"{self.epochBlocksMined}", fs, col1X, row2Y, ImageColor.getrgb(currentminedcolor))
        vicarioustext.drawtoprighttext(self.draw, "Retarget: ",              fs, col2X, row1Y, ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoplefttext(self.draw, f"{nextAdjustment}%",       fs, col2X, row1Y, ImageColor.getrgb(adjustcolor))
        vicarioustext.drawtoprighttext(self.draw, "In: ",                    fs, col2X, row2Y, ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoplefttext(self.draw, f"{nextEpochDescription}",  fs, col2X, row2Y, ImageColor.getrgb(self.textColor))


        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = DifficultyEpochPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Renders a representation of progress through the current difficulty epoch")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    