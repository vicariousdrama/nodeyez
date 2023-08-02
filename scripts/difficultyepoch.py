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
        if vicariousbitcoin.prunedBlockHeight is None:
            vicariousbitcoin.setPrunedBlockHeight()

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blockheight = vicariousbitcoin.getcurrentblock()
        self.epochFirstBlock = vicariousbitcoin.getfirstblockforepoch(self.blockheight)

        if vicariousbitcoin.prunedBlockHeight == 0 or \
            vicariousbitcoin.prunedBlockHeight <= self.epochFirstBlock:
            j = vicariousbitcoin.getblock(self.epochFirstBlock)
            self.epochBlocksMined = int(j["confirmations"])
            self.epochBeganTime = int(j["time"])
            self.usingPrunedData = False
        else:
            # estimate based on pruned data
            self.usingPrunedData = True
            j = vicariousbitcoin.getblock(vicariousbitcoin.prunedBlockHeight)
            self.epochBlocksMined = self.blockheight - self.epochFirstBlock + 1
            jTime = int(j["time"])
            currentTime = int(time.time())
            secondsPassed = currentTime - jTime
            secondsPerBlock = int(secondsPassed / (self.blockheight - vicariousbitcoin.prunedBlockHeight + 1))
            self.epochBeganTime = currentTime - (self.epochBlocksMined * secondsPerBlock)

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
        nextAdjustment += "%"
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
        if self.usingPrunedData: 
            nextAdjustment += " ?"
            nextEpochDescription += " ?"

        # tracking for labeling
        lastMinedX, lastMinedY, lastMinedBlock = -1, -1, -1
        lastAheadX, lastAheadY, lastAheadBlock = -1, -1, -1
        lastBehindX, lastBehindY, lastBehindBlock = -1, -1, -1
        prunedMaxY = -1
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
                blockBeingRendered = self.epochFirstBlock + epochblocknum - 1
                tlx = (padleft + (dc*blockw))
                tly = (padtop + (dr*blockw))
                brx = tlx+blockw-2
                bry = tly+blockw-2
                if epochblocknum <= self.epochBlocksMined:
                    fillcolor = self.minedColor                 # green
                    if epochblocknum > epochBlocksExpected:
                        fillcolor = self.aheadColor             # yellow
                        currentminedcolor = self.aheadColor     # yellow
                        if blockBeingRendered > lastAheadBlock:
                            lastAheadX = tlx
                            lastAheadY = tly
                            lastAheadBlock = blockBeingRendered
                    else:
                        if blockBeingRendered > lastMinedBlock:
                            lastMinedX = tlx
                            lastMinedY = tly
                            lastMinedBlock = blockBeingRendered
                    if self.usingPrunedData and blockBeingRendered < vicariousbitcoin.prunedBlockHeight:
                        prunedMaxY = bry if bry > prunedMaxY else prunedMaxY
                        blockInset = (brx-tlx)//3
                        tlx += blockInset
                        tly += blockInset
                        brx -= blockInset
                        bry -= blockInset
                        self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=ImageColor.getrgb(fillcolor))
                    else:
                        self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=ImageColor.getrgb(fillcolor))
                else:
                    outlinecolor = self.gridColor               # grey
                    if epochblocknum <= epochBlocksExpected:
                        outlinecolor = self.behindColor         # red
                        currentminedcolor = self.behindColor    # red
                        if blockBeingRendered > lastBehindBlock:
                            lastBehindX = tlx
                            lastBehindY = tly
                            lastBehindBlock = blockBeingRendered
                        self.draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=None,outline=ImageColor.getrgb(outlinecolor))
                    else: # dashed box
                        dllen = 2
                        dslen = 1
                        for dlx in range(tlx,brx,dllen): self.draw.line(xy=[(dlx,tly),(dlx+(dslen-1),tly)],fill=ImageColor.getrgb(outlinecolor),width=1)
                        for dly in range(tly,bry,dllen): self.draw.line(xy=[(brx,dly),(brx,dly+(dslen-1))],fill=ImageColor.getrgb(outlinecolor),width=1)
                        for dlx in range(brx,tlx,(-1*dllen)): self.draw.line(xy=[(dlx,bry),(dlx-(dslen-1),bry)],fill=ImageColor.getrgb(outlinecolor),width=1)
                        for dly in range(bry,tly,(-1*dllen)): self.draw.line(xy=[(tlx,dly),(tlx,dly-(dslen-1))],fill=ImageColor.getrgb(outlinecolor),width=1)

        # labels - key blocks
        if lastMinedBlock > -1:
            fs = int(self.height * (14/320))
            labelText = str(lastMinedBlock)
            labelX = lastMinedX
            if lastMinedY < (padtop + (2*blockw)):
                minedAnchor = "tr"
                labelY = lastMinedY + blockw + math.ceil(blockw/2)
                if lastMinedX < 100: minedAnchor = "tl"
            else:                
                minedAnchor = "br"
                labelY = lastMinedY - math.ceil(blockw/2)
                if lastMinedX < 100: minedAnchor = "bl"
            vicarioustext.drawLabel(draw=self.draw,s=labelText,fontsize=fs,anchorposition=minedAnchor,anchorx=labelX,anchory=labelY,textColor=self.minedColor)
        if lastBehindBlock > -1:
            fs = int(self.height * (14/320))
            labelText = str(lastBehindBlock)
            labelX = lastBehindX
            if lastBehindY > (padtop + ((gridRows-2)*blockw)):
                behindAnchor = "bl"
                labelY = lastBehindY - math.ceil(blockw/2)
                if lastBehindX > self.width - 100: behindAnchor = "br"
            else:                
                behindAnchor = "tl"
                labelY = lastBehindY + blockw + math.ceil(blockw/2)
                if lastBehindX > self.width - 100: behindAnchor = "tr"
            if lastMinedY != lastBehindY or minedAnchor[:1] != behindAnchor[:1]:
                vicarioustext.drawLabel(draw=self.draw,s=labelText,fontsize=fs,anchorposition=behindAnchor,anchorx=labelX,anchory=labelY,textColor=self.behindColor)
        if lastAheadBlock > -1:
            fs = int(self.height * (14/320))
            labelText = str(lastAheadBlock)
            labelX = lastAheadX
            if lastAheadY > (padtop + ((gridRows-2)*blockw)):
                aheadAnchor = "bl"
                labelY = lastAheadY - math.ceil(blockw/2)
                if lastAheadX > self.width - 100: aheadAnchor = "br"
            else:                
                aheadAnchor = "tl"
                labelY = lastAheadY + blockw + math.ceil(blockw/2)
                if lastAheadX > self.width - 100: aheadAnchor = "tr"
            if lastMinedY != lastAheadY or minedAnchor[:1] != aheadAnchor[:1]:
                vicarioustext.drawLabel(draw=self.draw,s=labelText,fontsize=fs,anchorposition=aheadAnchor,anchorx=labelX,anchory=labelY,textColor=self.aheadColor)

        # labels for pruned mode
        if self.usingPrunedData:
            fs = int(self.height * (10/320))
            blockMaxY = max([0,lastBehindY,lastMinedY,lastAheadY]) + blockw
            blockMinY = min(set([self.height,lastBehindY,lastMinedY,lastAheadY]).symmetric_difference(set([-1])))
            gridBottom = self.getInsetTop() + (gridRows*blockw)
            spaceNeeded = fs*6
            ly = 0
            if (prunedMaxY - self.getInsetTop() > spaceNeeded):
                # labels overlap pruned blocks at top
                ly = self.getInsetTop() + ((prunedMaxY - self.getInsetTop())//2)
            elif (gridBottom - blockMaxY > spaceNeeded):
                # labels in unmined blocks area
                ly = blockMaxY + ((gridBottom - blockMaxY)//2)
            elif (blockMaxY - blockMinY > spaceNeeded):
                # labels on blocks mined/expected area between ranges
                ly = blockMinY + ((blockMaxY-blockMinY)//2)
            elif (blockMinY - prunedMaxY > spaceNeeded):
                # labels below pruned blocks and above recent mined/expected
                ly = prunedMaxY + ((blockMinY - prunedMaxY)//2)
            else:
                # labels overlap pruned to mined/expected
                ly = self.getInsetTop() + ((blockMinY - self.getInsetTop())//2)
            lt = f"Node is pruned to block height {vicariousbitcoin.prunedBlockHeight}"
            vicarioustext.drawLabel(draw=self.draw,s=lt,fontsize=fs,anchorposition="b",anchorx=self.width//2,anchory=ly-1)
            lt = f"Expected mined and Retarget info will lose accuracy as a result"
            vicarioustext.drawLabel(draw=self.draw,s=lt,fontsize=fs,anchorposition="t",anchorx=self.width//2,anchory=ly+1)

        # labels - general
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
        vicarioustext.drawtoplefttext(self.draw, f"{nextAdjustment}",        fs, col2X, row1Y, ImageColor.getrgb(adjustcolor))
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