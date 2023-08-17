#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import json
import math
import os
import sys
import time
import vicariousbitcoin
import vicariouschart
import vicarioustext

class FeeEstimatesPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Fee Estimates panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # panel specific key names
            "graphAverageColor": "graphAverageColor",
            "graphBorderColor": "graphBorderColor",
            "graphDataColors": "graphDataColors",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dataHistory", [])
        self._defaultattr("graphAverageColor", "#8888ff")
        self._defaultattr("graphBorderColor", "#888888")        # used for graphs for feerates and segwit
        self._defaultattr("graphDataColors", ["#ff0000","#ffff00","#00ff00","#0000ff","#404040"])
        self._defaultattr("headerText", "Bitcoin Core Fee Estimates")
        self._defaultattr("interval", 15)

        # Initialize
        super().__init__(name="feeestimates")
        self.baseHeaderText = self.headerText
        self.minimumInterval = 10

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self._updateFeeEstimateHistory()

    def _loadFeeEstimateHistory(self):
        self.dataHistory = []
        fn = self.dataDirectory + "feeestimateshistory.json"
        if os.path.exists(fn):
            with open(fn, "r") as f:
                self.dataHistory = json.load(f)

    def _saveFeeEstimateHistory(self):
        fn = self.dataDirectory + "feeestimateshistory.json"
        with open(fn, "w") as f:
            json.dump(self.dataHistory, f)

    def _updateFeeEstimateHistory(self):
        # load if empty
        if len(self.dataHistory) == 0:
            self._loadFeeEstimateHistory()
        # get current fee estimate
        currenttime = int(time.time())
        nextblock = vicariousbitcoin.getcurrentblock() + 1
        item = {"time":currenttime,"targetblock":nextblock}
        blockTargets = [1,3,6,144]
        for blockTarget in blockTargets:
            feerate, blocks = vicariousbitcoin.getestimatesmartfee(blockTarget)
            feerate = (feerate * 100000000 / 1024)   # convert to sats/vB
            item[f"feerate{blockTarget}"] = feerate
            item[f"blocks{blockTarget}"] = blocks
        # add it
        self.dataHistory.append(item)
        # dont hold more then 40320 entries
        # 40320 = every 30 seconds * 2 weeks
        itemstoremove = len(self.dataHistory) - 40320
        if itemstoremove > 0:
            self.dataHistory = self.dataHistory[itemstoremove:]
            self._saveFeeEstimateHistory()
        elif len(self.dataHistory) % 10 == 0:
            self._saveFeeEstimateHistory()

    def run(self):

        dataNeeded = 10
        dataLength = len(self.dataHistory)
        if dataLength == 0:
            self.log(f"Unable to render Fee Estimates image. There is no data history")
            self.lastRan = int(time.time())
            return
        if dataLength < dataNeeded:
            self.log(f"Collecting {dataNeeded-dataLength} more data points before rendering")
            self.lastRan = int(time.time())
            return

        # Set header based on next block fee rate
        currentfee = self.dataHistory[-1]["feerate1"]
        currentfee = float(int(currentfee*100))/100
        self.headerText = f"{self.baseHeaderText}          |{currentfee}/vB"

        # Start image
        super().startImage()

        insetTop = self.getInsetTop()
        insetHeight = self.getInsetHeight()
        insetBottom = self.getInsetBottom()

        # Fit our chart data, grouping as necessary
        chartGrouping = max(len(self.dataHistory) // self.width, 1)
        chartList=self.dataHistory[-240:] #[(-1 * chartGrouping * 144):]
        # Get last block target
        blocknum = self.dataHistory[-1]["targetblock"]
        bottomBuffer = 32
        maxoffset=3

        # Calculate the low range value that should be used for all charts
        low, high, _, _, _ = vicariouschart.getFieldMinMaxAvgValues(chartList, "feerate144")
        difference = high - low
        units = int(math.pow(10, len(str(difference)) - 1))
        #chartHigh = int(math.ceil(high / units) * units)
        chartLow = int(math.floor(low / units) * units)
        #if chartHigh - (units//2) >= high: chartHigh -= (units//2)
        if chartLow + (units//2) <= low: chartLow += (units//2)

        # Draw 1 block
        offset=0
        chartHigh, chartLow, chartLeft, chartWidth = vicariouschart.drawBarChart(draw=self.draw, 
            left=0+offset, top=insetTop+offset,
            width=self.width-maxoffset, height=insetHeight-bottomBuffer,
            theList=chartList, fieldName="feerate1",
            showLabels=False, chartLabel=None, grouping=chartGrouping,
            valueColor=self.graphDataColors[0],
            averageColor=self.graphAverageColor, 
            borderColor=self.graphBorderColor,showGridLines=True, forceLow=chartLow)
        
        # Draw 3 block target
        offset=0 #1
        vicariouschart.drawBarChart(draw=self.draw, 
            left=0+offset, top=insetTop+offset,
            width=self.width-maxoffset, height=insetHeight-bottomBuffer,
            theList=chartList, fieldName="feerate3",
            showLabels=False, chartLabel=None, grouping=chartGrouping,
            valueColor=self.graphDataColors[1],
            showAverage=False, averageColor=self.graphAverageColor, 
            borderColor=self.graphBorderColor,showGridLines=True,
            forceHigh=chartHigh, forceLow=chartLow)

        # Draw 6 block target
        offset=0 #2
        vicariouschart.drawBarChart(draw=self.draw, 
            left=0+offset, top=insetTop+offset,
            width=self.width-maxoffset, height=insetHeight-bottomBuffer,
            theList=chartList, fieldName="feerate6",
            showLabels=False, chartLabel=None, grouping=chartGrouping,
            valueColor=self.graphDataColors[2],
            showAverage=False, averageColor=self.graphAverageColor, 
            borderColor=self.graphBorderColor,showGridLines=True,
            forceHigh=chartHigh, forceLow=chartLow)

        # Draw 144 block target
        offset=0 #3
        vicariouschart.drawBarChart(draw=self.draw, 
            left=0+offset, top=insetTop+offset,
            width=self.width-maxoffset, height=insetHeight-bottomBuffer,
            theList=chartList, fieldName="feerate144",
            showLabels=False, chartLabel=None, grouping=chartGrouping,
            valueColor=self.graphDataColors[3],
            showAverage=False, averageColor=self.graphAverageColor, 
            borderColor=self.graphBorderColor,showGridLines=True,
            forceHigh=chartHigh, forceLow=chartLow)

        # Draw block labels
        lineColor=ImageColor.getrgb(self.graphDataColors[4])
        blockLabelX = self.width
        blockLabelY = insetBottom - bottomBuffer + 7
        blockLabelWidth = 50
        l = len(chartList)
        xwidth = chartWidth // l
        xhalfwidth = (xwidth // 2) - 1  # for calculating bar width
        for i in range(l-1,0,-1):
            curblocknum = chartList[i]["targetblock"]
            if curblocknum == blocknum: continue
            # calculate x
            px = (i+1)/l
            lx = chartLeft + xhalfwidth + int((chartWidth-xwidth) * px) + 1
            # draw line
            self.draw.line(xy=(lx,insetTop,lx,insetBottom-12),fill=lineColor,width=1)
            # ensure label is left aligned to block start
            lx += 2 # space for label border
            # render blocknum if there is enough room
            if lx + blockLabelWidth < blockLabelX:
                blockLabelX = lx
                vicariouschart.drawLabel(draw=self.draw,s=f"{blocknum}",fontsize=10,anchorposition="tl",anchorx=blockLabelX,anchory=blockLabelY)
            # set the blocknum
            blocknum = curblocknum

        # Draw legend for colors
        legendDefs = [["1 Block (next)","1"],["3 Blocks (30 mins)","3"],["6 Blocks (1 hour)","6"],["144 Blocks (1 day)","144"]]
        legendFontSize = 10
        legendBoxSize = 11
        legendX = 55
        legendY = insetBottom - bottomBuffer - 4 - ((len(legendDefs)-1) * legendBoxSize * 2)
        legendNumber = -1
        for legendDef in legendDefs:
            legendNumber += 1
            legendName = legendDef[0]
            legendData = legendDef[1]
            legendFeerate = self.dataHistory[-1][f"feerate{legendData}"]
            legendFeerate = float(int(legendFeerate*100))/100
            legendBlocks = self.dataHistory[-1][f"blocks{legendData}"]
            legendLabel = f"    Fee Rate for {legendName} target = {legendFeerate} sats/vB"
            vicarioustext.gettextdimensions(self.draw, legendLabel, legendFontSize, False)
            vicariouschart.drawLabel(self.draw, legendLabel, legendFontSize, "bl", legendX, legendY)
            self.draw.rectangle(xy=[(legendX,legendY-legendBoxSize),(legendX+legendBoxSize,legendY)],fill=self.graphDataColors[legendNumber],outline=ImageColor.getrgb(self.graphBorderColor),width=1)
            #legendX += legendw + 10
            legendY += legendBoxSize * 2

        # Finish image
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = FeeEstimatesPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg0 = sys.argv[0]
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces a graph of the fee estimates reported by Bitcoin node over time")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    
