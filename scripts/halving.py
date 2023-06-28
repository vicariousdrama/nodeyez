#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw, ImageOps
from datetime import datetime
from vicariouspanel import NodeyezPanel
import glob
import json
import os
import random
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

class HalvingPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Fear and Greed panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorGrid": "gridColor",
            "colorProgress": "progressColor",
            "colorTextFG": "textColor",
            "fillGridDividersEnabled": "gridDividerFillEnabled",
            "gridImageUnmined": "gridImageUnminedMode",
            "sleepInterval": "interval",
            # panel specific key names
            "gridColor": "gridColor",
            "gridDividerFillEnabled": "gridDividerFillEnabled",
            "gridImageEnabled": "gridImageEnabled",
            "gridImageUnminedMode": "gridImageUnminedMode",
            "progressColor": "progressColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("backgroundColor", "#000000")
        self._defaultattr("gridColor", "#404040")
        self._defaultattr("gridDividerFillEnabled", True)
        self._defaultattr("gridImageEnabled", True)
        self._defaultattr("gridImageUnminedMode", "grayscale")
        self._defaultattr("headerText", "|Next Halving|?")
        self._defaultattr("interval", 540)
        self._defaultattr("progressColor", "#ffaa00")
        self._defaultattr("watermarkAnchor", "topleft")

        # Initialize
        super().__init__(name="halving")

    def blockclockReport(self):
        baseapi=f"http://{self.blockclockAddress}/api/"

        # TODO: integrate bctext
        #   BLOC K.... .789 000. ..IS.. .69. 420%
        #    OF   THE   WAY  TO   NEXT  HALV ING
        halvingInterval = 210000
        halvings = self.blockheight // halvingInterval
        halvingbegin = halvings * halvingInterval + 1
        halvingPercent = float(self.blockheight - halvingbegin) / float(2100)
        halvingPercentText = str(format(halvingPercent, ".3f")) + "%"
        bh = str(self.blockheight)
        sd = bh[-4:]
        td = str("...." + bh[0:-4])[-4:]
        dp = halvingPercentText[-3:]
        ip = halvingPercentText[0:-3]
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/0/BLOC/OF", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/1/K..../THE", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/2/{td}/WAY", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/3/{sd}/TO", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/4/IS/NEXT", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/5/{ip}/HALV", self.blockclockPassword)
        vicariousnetwork.getblockclockapicall(baseapi + f"ou_text/6/{dp}%/ING..", self.blockclockPassword)

    def isDependenciesMet(self):
        return True

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blockheight = vicariousbitcoin.getcurrentblock()
        j = vicariousbitcoin.getblock(vicariousbitcoin.getfirstblockforhalving(self.blockheight))
        self.halvingBlocksMined = int(j["confirmations"]) + 1
        self.halvingBeganTime = int(j["time"])

    def _getGridImage(self, p):
        ipfsDirectory = f"{self.dataDirectory}ipfs/"
        filegood = False
        if os.path.exists(ipfsDirectory):
            random.seed(p * 11235813)   # consistently deterministic
            filegood = False
            fileattempts = 5
            while ((not filegood) and (fileattempts > 0)):
                filename = random.choice(os.listdir(ipfsDirectory))
                try:
                    filepath = f"{ipfsDirectory}{filename}"
                    filesize = os.path.getsize(filepath)
                    if filesize > 50000:
                        self.log(f"loading image file {filepath}")
                        rImage = Image.open(filepath).convert("RGBA")
                        filegood = True
                except BaseException as err:
                    # not sure what
                    self.log(f"error loading image: {err}")
                    fileattempts = fileattempts -1
        if not filegood:
            rImage = Image.open("../images/logo.png").convert("RGBA")
        return rImage

    def run(self):
        if not self.isDependenciesMet():
            self._markAsRan()
            return

        super().startImage()
        centerX = self.width // 2
        centerY = self.height // 2
        halvingInterval = 210000
        gridRows = 35 # x 60 = 2100.  2100 is blocks for 1% of the halvingInterval
        gridCols = 60
        halvings = self.blockheight // halvingInterval
        halvingbegin = halvings * halvingInterval + 1
        halvingend = (halvings + 1) * halvingInterval
        halvingPercent = float(self.blockheight - halvingbegin) / float(gridRows * gridCols)
        halvingPercentText = str(format(halvingPercent, ".3f")) + "%"
        self.headerText = f"|Next Halving|{halvingPercentText}"
        gridblocks = self.blockheight % (gridRows * gridCols)
        # grid for the current percent
        blockw = ((self.width-1)//gridCols)
        gridLeft= (self.width-(gridCols*blockw)) // 2
        gridTop = self.getInsetTop()
        gridRight = self.width - gridLeft
        gridBottom = gridTop + (gridRows * blockw)

        if self.gridImageEnabled:
            gridw = blockw * gridCols
            gridh = blockw * gridRows
            gridratio=float(gridw)/float(gridh)
            gridImage = self._getGridImage(int(halvingPercent))
            gridImageWidth = int(gridImage.getbbox()[2])
            gridImageHeight = int(gridImage.getbbox()[3])
            gridImageRatio = float(gridImageWidth)/float(gridImageHeight)
            if gridImageRatio > gridratio:
                newgridImageHeighteight=int(gridImageWidth/gridratio)
                gridImageOffset = int((newgridImageHeighteight-gridImageHeight)/2)
                gridImageTaller = Image.new(mode="RGBA", size=(gridImageWidth, newgridImageHeighteight), color=ImageColor.getrgb(self.progressColor))
                gridImageTaller.paste(gridImage, (0,gridImageOffset))
                gridImage.close()
                gridImage = gridImageTaller.resize(size=(gridw,gridh))
                gridImageTaller.close()
            else:
                newgridImageWidthidth=int(gridImageHeight*gridratio)
                gridImageOffset = int((newgridImageWidthidth-gridImageWidth)/2)
                gridImageWider = Image.new(mode="RGBA", size=(newgridImageWidthidth, gridImageHeight), color=ImageColor.getrgb(self.progressColor))
                gridImageWider.paste(gridImage, (gridImageOffset,0))
                gridImage.close()
                gridImage = gridImageWider.resize(size=(gridw,gridh))
                gridImageWider.close()
            gridImageUnmined = gridImage.copy()
            if self.gridImageUnminedMode == 'grayscale':
                gridImageUnmined = ImageOps.grayscale(gridImageUnmined)
            if self.gridImageUnminedMode == 'dither':
                gridImageUnmined = gridImageUnmined.convert('1')
            if self.gridImageUnminedMode == 'dither2':
                gridImageUnmined = gridImageUnmined.convert('L')
        for dc in range(gridCols):
            for dr in range(gridRows):
                gridblocknum = ((dr*gridCols)+dc)+1
                tlx = (gridLeft + (dc*blockw))
                tly = (gridTop + (dr*blockw))
                brx = tlx+blockw-2
                bry = tly+blockw-2
                fillcolor = None
                outlinecolor = self.gridColor
                if gridblocknum <= gridblocks:
                    fillcolor = self.progressColor
                    outlinecolor = None
                if self.gridImageEnabled:
                    # crop from gridimage
                    gtlx = (dc*blockw)
                    gtly = (dr*blockw)
                    gbrx = gtlx+blockw-1
                    gbry = gtly+blockw-1
                    if fillcolor != self.progressColor:
                        gblockimg = gridImageUnmined.crop((gtlx,gtly,gbrx,gbry))
                    else:
                        if self.gridDividerFillEnabled:
                            gbrx += 1
                            gbry += 1
                        gblockimg = gridImage.crop((gtlx,gtly,gbrx,gbry))
                    # paste the part into the right spot
                    self.canvas.paste(gblockimg, (tlx, tly))
                    # cleanup resources
                    gblockimg.close()
                    # highlight current block in the grid with an outline
                    if gridblocknum == gridblocks:
                        fillcolor = None
                        outlinecolor = self.progressColor
                        self.draw.rectangle(xy=((tlx-1,tly-1),(brx+1,bry+1)),fill=fillcolor,outline=outlinecolor,width=2)
                else:
                    if self.gridDividerFillEnabled:
                        brx += 1
                        bry += 1
                    self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=fillcolor,outline=outlinecolor)
        # annotation of grid representation
        afs = int(self.height * 10/320)
        vicarioustext.drawtoprighttext(self.draw, "grid represents 1 whole percent", afs, gridRight, gridBottom + 2, ImageColor.getrgb(self.progressColor))

        # progress bar showing visual block progression
        barPad    = 2
        barLeft   = barPad
        barTop    = self.height - (self.getFooterHeight() * 2)
        barTop    = gridBottom + afs + barPad if barTop <= gridBottom + afs + barPad else barTop
        barRight  = self.width - self.getFooterWidth() - barPad
        barBottom = self.height - barPad
        # outline portion
        self.draw.rounded_rectangle(xy=(barLeft,barTop,barRight,barBottom),radius=3,fill=None,outline=ImageColor.getrgb(self.gridColor),width=1)
        # fill portion
        barHeight = barBottom - barTop - (barPad*2)
        barWidthAvailable = barRight - barLeft - (barPad*2)
        barWidth  = (int(float(barWidthAvailable) * halvingPercent / 100.00))
        barWidthX = barLeft+barPad+barWidth
        barWidthX = barRight-barPad if barWidthX > barRight - barPad else barWidthX
        self.draw.rounded_rectangle(xy=(barLeft+barPad,barTop+barPad,barWidthX,barBottom-barPad),radius=3,fill=ImageColor.getrgb(self.progressColor))
        # annotation of block number
        blocksToGo = halvingend + 1 - self.blockheight
        currentTime = int(time.time())
        secondsPassed = currentTime - self.halvingBeganTime
        avgBlockTime = 600 if self.halvingBeganTime == 0 else secondsPassed / self.halvingBlocksMined
        secondsRemain = avgBlockTime * blocksToGo
        if blocksToGo % 4 == 0:
            # block height
            blockText = f"BLOCK {self.blockheight}"
        elif blocksToGo % 4 == 1:
            # blocks to go
            blockText = f"{blocksToGo} BLOCKS TO GO"
        elif blocksToGo % 4 == 2:
            # approximate duration until halving
            yearsUntilHalving = secondsRemain // (60 * 60 * 24 * 365)
            monthsUntilHalving = int(secondsRemain // (60 * 60 * 24 * 30))
            weeksUntilHalving = int(secondsRemain // (60 * 60 * 24 * 7))
            daysUntilHalving = int(secondsRemain // (60 * 60 * 24))
            hoursUntilHalving = int(secondsRemain // (60 * 60))
            if yearsUntilHalving > 1:
                blockText = f"OVER {yearsUntilHalving} YEARS TO GO"
            elif monthsUntilHalving == 18:
                blockText = f"~ A YEAR AND A HALF TO GO"
            elif monthsUntilHalving == 12:
                blockText = f"~ 1 YEAR TO GO"
            elif monthsUntilHalving == 6:
                blockText = f"~ HALF A YEAR TO GO"
            elif monthsUntilHalving > 2:
                blockText = f"~ {monthsUntilHalving} MONTHS TO GO"
            elif weeksUntilHalving > 2:
                blockText = f"~ {weeksUntilHalving} WEEKS TO GO"
            elif daysUntilHalving > 2:
                blockText = f"~ {daysUntilHalving} DAYS TO GO"
            elif hoursUntilHalving > 2:
                blockText = f"~ {hoursUntilHalving} HOURS TO GO"
            else:
                blockText = f"{blocksToGo} BLOCKS TO GO"
        elif blocksToGo % 4 == 3:
            # approximate date of halving
            if blocksToGo < 2016:
                blockText = f"{blocksToGo} BLOCKS TO GO"
            else:
                projectedDate = datetime.fromtimestamp(currentTime + secondsRemain)
                projectedDateText = projectedDate.strftime("%Y-%m-%d")
                blockText = f"Halving ETA: {projectedDateText}"
        blockFontSize = self.getFooterHeight()
        blockFontSize, _, _ = vicarioustext.getmaxfontsize(draw=self.draw, s=blockText, maxwidth=(barWidthAvailable//2), maxheight=barHeight, isbold=True, maxfontsize=blockFontSize, minfontsize=8)
        sw, sh, f = vicarioustext.gettextdimensions(draw=self.draw, s=blockText, fontsize=blockFontSize, isbold=True)
        if sw < (barWidthX - barPad):
            # on the progress
            vicarioustext.drawrighttext(self.draw, blockText, blockFontSize, barWidthX - barPad, barTop + (barBottom-barTop)//2, ImageColor.getrgb(self.backgroundColor), True)
        else:
            # to the right of bar
            vicarioustext.drawlefttext(self.draw, blockText, blockFontSize, barWidthX + barPad, barTop + (barBottom-barTop)//2, ImageColor.getrgb(self.progressColor), True)

        # cleanup image resources
        if self.gridImageEnabled:
            gridImage.close()
            gridImageUnmined.close()
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = HalvingPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Renders a representation of progress through the current halving period")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    