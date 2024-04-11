#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import locale
import math
import sys
import vicariousnetwork
import vicarioustext

class MempoolSpacePanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Mempool Space panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "blockSatLevels": "blockSatRangeColors",
            "blocksToRender": "renderMaximumBlocks",
            "colorBackground": "backgroundColor",
            "colorBlockEdgeOutline": "blockEdgeColor",
            "colorBlockFace": "blockFaceColor",
            "colorBlockSide": "blockSideColor",
            "colorBlockTop": "blockTopColor",
            "colorTextFG": "textColor",
            "histogramSatLevels": "histogramSatRangeColors",
            "renderStyle": "renderDirection",
            "sleepInterval": "interval",
            "urlfeehistogram": "feeHistogramUrl",
            "urlfeerecs": "feeRecommendationsUrl",
            "urlmempool": "mempoolBlocksUrl",
            # panel specific key names
            "attributionColor": "attributionColor",
            "blockEdgeColor": "blockEdgeColor",
            "blockFaceColor": "blockFaceColor",
            "blockSatRangeColors": "blockSatRangeColors",
            "blockSideColor": "blockSideColor",
            "blockTopColor": "blockTopColor",
            "feeHistogramUrl": "feeHistogramUrl",
            "feeRecommendationsUrl": "feeRecommendationsUrl",
            "histogramSatRangeColors": "histogramSatRangeColors",
            "mempoolBlocksUrl": "mempoolBlocksUrl",
            "renderDirection": "renderDirection",
            "renderMaximumBlocks": "renderMaximumBlocks",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#4cbae6")
        self._defaultattr("blockEdgeColor", "#202020")
        self._defaultattr("blockFaceColor", "#606060")
        self._defaultattr("blockSatRangeColors", [
            {"satMin": 0.0, "satMax": 10.0, "blockColor": "#40c040", "textColor": "#ffffff"},
            {"satMin": 10.0, "satMax": 30.0, "blockColor": "#9ea90b", "textColor": "#ffffff"},
            {"satMin": 30.0, "satMax": 60.0, "blockColor": "#d1ac08", "textColor": "#ffffff"},
            {"satMin": 60.0, "satMax": 100.0, "blockColor": "#f4511e", "textColor": "#ffffff"},
            {"satMin": 100.0, "satMax": 150.0, "blockColor": "#b71c1c", "textColor": "#ffffff"},
            {"satMin": 150.0, "satMax": 9999.0, "blockColor": "#4a148c", "textColor": "#ffffff"}
        ])
        self._defaultattr("blockSideColor", "#404040")
        self._defaultattr("blockTopColor",  "#505050")
        self._defaultattr("feeHistogramData", {"count":0,"vsize":0,"total_fee":0,"fee_histogram":[]})
        self._defaultattr("feeHistogramUrl", "https://mempool.space/api/mempool")
        self._defaultattr("feeRecommendationsUrl", "https://mempool.space/api/v1/fees/recommended")
        self._defaultattr("headerText", "Mempool Fees")
        self._defaultattr("histogramSatRangeColors", [
            {"satMin": 0.0, "satMax": 2.0, "fillColor": "#d81b60"},
            {"satMin": 2.0, "satMax": 3.0, "fillColor": "#8e24aa"},
            {"satMin": 3.0, "satMax": 4.0, "fillColor": "#5e35b1"},
            {"satMin": 4.0, "satMax": 5.0, "fillColor": "#3949ab"},
            {"satMin": 5.0, "satMax": 6.0, "fillColor": "#1e88e5"},
            {"satMin": 6.0, "satMax": 8.0, "fillColor": "#039be5"},
            {"satMin": 8.0, "satMax": 10.0, "fillColor": "#00acc1"},
            {"satMin": 10.0, "satMax": 12.0, "fillColor": "#00897b"},
            {"satMin": 12.0, "satMax": 15.0, "fillColor": "#43a047"},
            {"satMin": 15.0, "satMax": 20.0, "fillColor": "#7cb342"},
            {"satMin": 20.0, "satMax": 30.0, "fillColor": "#c0ca33"},
            {"satMin": 30.0, "satMax": 40.0, "fillColor": "#fdd835"},
            {"satMin": 40.0, "satMax": 50.0, "fillColor": "#ffb300"},
            {"satMin": 50.0, "satMax": 60.0, "fillColor": "#fb8c00"},
            {"satMin": 60.0, "satMax": 70.0, "fillColor": "#f4511e"},
            {"satMin": 70.0, "satMax": 80.0, "fillColor": "#6d4c41"},
            {"satMin": 80.0, "satMax": 90.0, "fillColor": "#757575"},
            {"satMin": 90.0, "satMax": 100.0, "fillColor": "#546e7a"},
            {"satMin": 100.0, "satMax": 125.0, "fillColor": "#b71c1c"},
            {"satMin": 125.0, "satMax": 150.0, "fillColor": "#880e4f"},
            {"satMin": 150.0, "satMax": 9999.0, "fillColor": "#4a148c"}
        ])
        self._defaultattr("interval", 300)
        self._defaultattr("mempoolBlocksData", [])
        self._defaultattr("mempoolBlocksUrl", "https://mempool.space/api/v1/fees/mempool-blocks")
        self._defaultattr("renderDirection", "righttoleft")
        self._defaultattr("renderMaximumBlocks", 3)
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "topleft")

        # Initialize
        super().__init__(name="mempoolspace")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.log("Fetching mempool blocks")
        mempoolData = vicariousnetwork.getmempoolblocks(self.useTor, self.mempoolBlocksUrl)
        if mempoolData != []:
            if self.mempoolBlocksData != mempoolData:
                self.mempoolBlocksData = mempoolData

        self.log("Fetching mempool histogram info")
        histogramData = vicariousnetwork.getmempoolhistograminfo(self.useTor, self.feeHistogramUrl)
        if histogramData != {"count":-1,"vsize":0,"total_fee":0,"fee_histogram":[]}:
            if self.feeHistogramData != histogramData:
                self.feeHistogramData = histogramData

        self.log("Fetching mempool recommended fees")
        fastestFee, halfHourFee, hourFee, minimumFee = vicariousnetwork.getmempoolrecommendedfees(self.useTor, self.feeRecommendationsUrl)
        if fastestFee != -1: self.fastestFee = fastestFee
        if halfHourFee != -1: self.halfHourFee = halfHourFee
        if hourFee != -1: self.hourFee = hourFee
        if minimumFee != -1: self.minimumFee = minimumFee
        if not hasattr(self, "fastestFee"): self.fastestFee = "?"
        if not hasattr(self, "halfHourFee"): self.halfHourFee = "?"
        if not hasattr(self, "hourFee"): self.hourFee = "?"
        if not hasattr(self, "minimumFee"): self.minimumFee = "?"

    def _getColorsForBlock(self, satfee):
        satFee = float(satfee)
        b = "#404040"
        t = "#ffffff"
        for x in self.blockSatRangeColors:
            satMin = float(0.0)
            satMax = float(0.0)
            if "satMin" in x: satMin = float(x["satMin"])
            if "satMax" in x: satMax = float(x["satMax"])
            if satMin <= float(satFee):
                if satMax >= float(satFee):
                    if "blockColor" in x: b = x["blockColor"]
                    if "colorBlock" in x: b = x["colorBlock"] # backwards compatible
                    if "textColor" in x: t = x["textColor"]
                    if "colorText" in x: t = x["colorText"] # backwards compatible
        return b, t

    def _getColorForHistogram(self, satFee):
        f = "#404040"
        for x in self.histogramSatRangeColors:
            if "satMin" in x and float(x["satMin"]) <= float(satFee):
                if "satMax" in x and float(x["satMax"]) >= float(satFee):
                    if "fillColor" in x: f = x["fillColor"]
                    if "colorFill" in x: f = x["colorFill"] # backwards compatible
        return f

    def _getHumanReadableSize(self, sizeInBytes):
        if sizeInBytes == 0:
            return "0B"
        unitAbbrev = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(sizeInBytes, 1024)))
        p = math.pow(1024, i)
        s = round(sizeInBytes / p, 2)
        return f"{s} {unitAbbrev[i]}"

    def _renderMempoolBlock(self, left, top, blockWidth, blockIndex, blockCount):
        blockInfo = self.mempoolBlocksData[blockIndex]
        blockSize=blockInfo["blockSize"]
        blockVSize=blockInfo["blockVSize"]
        transactions=int(blockInfo["nTx"])
        feeRanges=list(blockInfo["feeRange"])
        feeLow=feeRanges[0]
        feeHigh=feeRanges[len(feeRanges)-1]
        feeMedian=blockInfo["medianFee"]
        blockFaceColor, blockTextColor = self._getColorsForBlock(feeMedian)
        feeLowInt = int(math.floor(float(feeLow)))
        feeHighInt = int(math.ceil(float(feeHigh)))
        feeMedianInt = int(math.floor(float(feeMedian)))
        blockDepth=(blockWidth*14)//100
        pad=2
        descriptorSatVB = f"~{feeMedianInt} sat/vB"
        descriptorSatRange = f"({feeLowInt} - {feeHighInt})"
        descriptorTx = f"{transactions:,d} transactions"
        descriptorTx2 = f"{transactions:,d} tx"
        descriptorETA = f"In ~{((blockIndex+1)*10)} minutes"
        descriptorETA2 = f"~{((blockIndex+1)*10)} mins"
        descriptorSize = self._getHumanReadableSize(int(blockSize))

        # side
        self.draw.polygon(xy=((left+pad,top+pad),(left+pad,top+blockWidth-pad-blockDepth),(left+pad+blockDepth,top+blockWidth-pad),(left+pad+blockDepth,top+pad+blockDepth)),outline=ImageColor.getrgb(self.blockEdgeColor),fill=ImageColor.getrgb(self.blockSideColor))
        # top
        self.draw.polygon(xy=((left+pad,top+pad),(left+pad+blockDepth,top+pad+blockDepth),(left+blockWidth-pad,top+pad+blockDepth),(left+blockWidth-pad-blockDepth,top+pad)),outline=ImageColor.getrgb(self.blockEdgeColor),fill=ImageColor.getrgb(self.blockTopColor))
        # face
        self.draw.polygon(xy=((left+pad+blockDepth,top+pad+blockDepth),(left+blockWidth-pad,top+pad+blockDepth),(left+blockWidth-pad,top+blockWidth-pad),(left+pad+blockDepth,top+blockWidth-pad)),outline=ImageColor.getrgb(self.blockEdgeColor),fill=ImageColor.getrgb(self.blockFaceColor))
        # fill
        fillxstart=(left+blockWidth-pad)-int(float((left+blockWidth-pad)-(left+pad+blockDepth))*float(float(blockVSize)/float(1000000))) # default (righttoleft)
        fillxend=(left+blockWidth-pad)
        if self.renderDirection == "lefttoright":
            fillxstart=left+pad+blockDepth
            fillxend=left+pad+blockDepth+int(float((left+blockWidth-pad)-(left+pad+blockDepth))*float(float(blockVSize)/float(1000000)))
        self.draw.polygon(xy=((fillxstart,top+pad+blockDepth),(fillxend,top+pad+blockDepth),(fillxend,top+blockWidth-pad),(fillxstart,top+blockWidth-pad)),outline=ImageColor.getrgb(self.blockEdgeColor),fill=ImageColor.getrgb(blockFaceColor))

        # Text labels
        centerx=left+blockDepth+((blockWidth-blockDepth)//2)
        if blockCount <= 3:
            fontSize = int(self.height * 14/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSatVB, fontSize, centerx, top+pad+(blockDepth*2),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorSatRange, fontSize, centerx, top+pad+(blockDepth*3),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorTx, fontSize, centerx, top+pad+(blockDepth*5),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorETA, fontSize, centerx, top+pad+(blockDepth*6),ImageColor.getrgb(blockTextColor))
            fontSize = int(self.height * 18/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSize, fontSize, centerx, top+pad+(blockDepth*4),ImageColor.getrgb(blockTextColor))
        if blockCount == 4:
            fontSize = int(self.height * 12/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSatVB, fontSize, centerx, top+pad+(blockDepth*2),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorSatRange, fontSize, centerx, top+pad+(blockDepth*3),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorTx2, fontSize, centerx, top+pad+(blockDepth*5),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorETA, fontSize, centerx, top+pad+(blockDepth*6),ImageColor.getrgb(blockTextColor))
            fontSize = int(self.height * 14/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSize, fontSize, centerx, top+pad+(blockDepth*4),ImageColor.getrgb(blockTextColor))
        if blockCount == 5:
            fontSize = int(self.height * 10/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSatVB, fontSize, centerx, top+pad+(blockDepth*2),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorSatRange, fontSize, centerx, top+pad+(blockDepth*3.3),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorETA2, fontSize, centerx, top+pad+(blockDepth*6),ImageColor.getrgb(blockTextColor))
            fontSize = int(self.height * 12/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorTx2, fontSize, centerx, top+pad+(blockDepth*4.6),ImageColor.getrgb(blockTextColor))
        if blockCount == 6:
            fontSize = int(self.height * 9/320)
            vicarioustext.drawcenteredtext(self.draw, descriptorSatVB, fontSize, centerx, top+pad+(blockDepth*2),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorSatRange, fontSize, centerx, top+pad+(blockDepth*4),ImageColor.getrgb(blockTextColor))
            vicarioustext.drawcenteredtext(self.draw, descriptorETA2, fontSize, centerx, top+pad+(blockDepth*6),ImageColor.getrgb(blockTextColor))

    def _renderHistogramBarSegment(self, blockWidth, currentHistVSize, currentHistSatFee, histX2, histY1, histY2):
        # bar
        histPixelWidth = int(float(blockWidth) * (float(currentHistVSize)/float(1000000)))
        histColor = self._getColorForHistogram(currentHistSatFee)
        histX1 = histX2 - histPixelWidth # default (righttoleft)
        if self.renderDirection == "lefttoright": histX1 = histX2 + histPixelWidth
        self.draw.polygon(xy=((histX1,histY1),(histX2,histY1),(histX2,histY2),(histX1,histY2)),outline=ImageColor.getrgb(self.blockEdgeColor), fill=ImageColor.getrgb(histColor))
        # text label
        alignCenter = False
        alignRight = True
        textY = histY1 + (histY2-histY1)//2
        fontSize = int(self.height * 10/320)
        texts = [f"{currentHistSatFee} sat/vB", f"{currentHistSatFee}"]
        textFits = False
        for text in texts:
            if textFits: break
            textWidth, _, _ = vicarioustext.gettextdimensions(self.draw, text, fontSize, False)
            if textWidth < histPixelWidth - 4:
                if alignCenter:
                    textX = histX1 + histPixelWidth//2 # default righttoleft
                    if self.renderDirection == "lefttoright": textX = histX2 + histPixelWidth//2
                    vicarioustext.drawcenteredtext(self.draw, text, fontSize, textX, textY)
                if alignRight:
                    textX = histX1 + histPixelWidth-2 # default righttoleft
                    if self.renderDirection == "lefttoright": textX = histX2 + textWidth + 2
                    vicarioustext.drawrighttext(self.draw, text, fontSize, textX, textY)
                textFits = True
        return histX1

    def _isMempoolSpace(self):
        sources = [self.mempoolBlocksUrl, self.feeHistogramUrl, self.feeRecommendationsUrl]
        for source in sources:
            if "mempool.space" in source: return True
            if "mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion" in source: return True
        return False

    def run(self):

        super().startImage()

        # render the blocks
        mempoolBlockList = list(self.mempoolBlocksData)
        mempoolBlockLength = len(mempoolBlockList)
        blockCount = self.renderMaximumBlocks
        if blockCount > mempoolBlockLength: blockCount = mempoolBlockLength
        if blockCount > 6: blockCount = 6
        if blockCount < 3: blockCount = 3
        blockWidth = self.width // blockCount
        totalVSize = 0  # will capture total during this pass
        totalTx = 0
        for mempoolBlockIndex in range(mempoolBlockLength):
            totalVSize += mempoolBlockList[mempoolBlockIndex]["blockVSize"]
            totalTx += mempoolBlockList[mempoolBlockIndex]["nTx"]
            if mempoolBlockIndex > (blockCount - 1): continue
            blockX = int(self.width - ((mempoolBlockIndex+1)*blockWidth))
            if self.renderDirection == "lefttoright": blockX = int(mempoolBlockIndex*blockWidth)
            self._renderMempoolBlock(blockX, self.getInsetTop(), blockWidth, mempoolBlockIndex, blockCount)

        # approx total of potential blocks and transactions
        fontSize = int(self.height * 12/320)
        totalBlocks = math.ceil(totalVSize / 1000000)
        totalETA = str(int(totalBlocks / 6)) + " hours" if totalBlocks > 12 else str(int(totalBlocks * 10)) + " minutes"
        totalSummary = f"{totalTx:,d} tx with vsize {self._getHumanReadableSize(totalVSize)}, ~{totalBlocks} blocks, ~{totalETA}"
        vicarioustext.drawcenteredtext(self.draw, totalSummary, fontSize, self.width//2, self.getInsetTop()+blockWidth+(self.getInsetTop() // 4), ImageColor.getrgb(self.textColor), False)

        # histogram info
        histY1=self.getInsetTop()+blockWidth+(self.getInsetTop()//2)
        histY2=histY1+self.getInsetTop()
        if histY2 <= self.getInsetTop() + self.getInsetHeight():
            histX1=0; histX2=self.width # default (righttoleft)
            if self.renderDirection == "lefttoright": histX1=self.width; histX2=0
            histList=list(self.feeHistogramData["fee_histogram"])
            histLength=len(histList)
            currentHistSatFee = 0 # to consolidate like fees
            currentHistVSize = 0
            for histIndex in range(histLength):
                histRender = False
                histSatFee = int(histList[histIndex][0])
                histVSize = int(histList[histIndex][1])
                if histIndex == 0:
                    currentHistSatFee = histSatFee; currentHistVSize = histVSize
                    if histLength == 1:
                        histRender = True
                    else:
                        if int(histList[histIndex+1][0]) != histSatFee:
                            histRender = True
                else:
                    if histSatFee == currentHistSatFee:
                        currentHistVSize += histVSize
                    else:
                        histRender = True
                if histRender:
                    histX1 = self._renderHistogramBarSegment(blockWidth,currentHistVSize,currentHistSatFee,histX2,histY1,histY2)
                    histX2 = histX1
                    currentHistSatFee = histSatFee; currentHistVSize = histVSize
                    if self.renderDirection == "righttoleft" and histX2 <= 0: break
                    if self.renderDirection == "lefttoright" and histX2 >= self.width: break
            histX1 = self._renderHistogramBarSegment(blockWidth,currentHistVSize,currentHistSatFee,histX2,histY1,histY2)

        # fee recommendations
        feeY1 = histY2 + 4
        feeY2 = feeY1 + self.getInsetTop()
        if feeY2 <= self.getInsetTop() + self.getInsetHeight():
            feeY = feeY1 + (feeY2-feeY1)//2
            feeFont1 = int(self.height * 18/320)
            feeFont2 = int(self.height * 16/320)
            feeRecList = [f"Minimum: {self.minimumFee}", f"1 Hour: {self.hourFee}", f"30 Minutes: {self.halfHourFee}", f"Next: {self.fastestFee}"]
            if self.renderDirection == "lefttoright": feeRecList.reverse()
            for feeRecIdx in range(len(feeRecList)):
                if feeRecIdx == 0:
                    vicarioustext.drawlefttext(self.draw, feeRecList[feeRecIdx], feeFont1, 0, feeY, ImageColor.getrgb(self.textColor))
                elif feeRecIdx == len(feeRecList) - 1:
                    vicarioustext.drawrighttext(self.draw, feeRecList[feeRecIdx], feeFont1, self.width, feeY, ImageColor.getrgb(self.textColor))
                else:
                    feeX = int(self.width / (len(feeRecList) * 2) * ((feeRecIdx * 2) + 1)) 
                    vicarioustext.drawcenteredtext(self.draw, feeRecList[feeRecIdx], feeFont2, feeX, feeY, ImageColor.getrgb(self.textColor))

        # attribution
        attY1 = feeY2 + 4
        attY2 = attY1 + self.getInsetTop()
        if attY2 <= self.getInsetTop() + self.getInsetHeight():
            text = "Data from sovereign node"
            if self._isMempoolSpace(): text = "Data from mempool.space"
            attFont = int(self.height * 16/320)
            attY = attY1 + (attY2-attY1)//2
            # vicarioustext.drawcenteredtext(self.draw, text, attFont, self.width//2, attY, ImageColor.getrgb(self.attributionColor))
            vicarioustext.drawbottomlefttext(self.draw, text, attFont, 0, self.height, ImageColor.getrgb(self.attributionColor))


        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = MempoolSpacePanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares an image depicting the upcoming blocks and fees in the Mempool")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    
