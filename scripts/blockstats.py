#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import json
import os
import sys
import time
import vicariousbitcoin
import vicariouschart
import vicarioustext

class BlockStatsPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Block Stats panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorBands": "graphDataColors",
            "colorGraphAverage": "graphAverageColor",
            "colorGraphOutline": "graphBorderColor",
            "colorShapeOutline": "shapeOutlineColor",
            "colorShapeShadow": "shapeShadowColor",
            "colorTextFG": "textColor",
            "logStatsForRanges": "reportStatsEnabled",
            "showFeeRates": "renderFeesImage",
            "showSegwitPrevalence": "renderSegwitImage",
            "showStatsBlock": "renderStatsImage",
            "sleepInterval": "interval",
            # panel specific key names
            "graphAverageColor": "graphAverageColor",
            "graphBorderColor": "graphBorderColor",
            "graphDataColors": "graphDataColors",
            "renderFeesImage": "renderFeesImage",
            "renderScriptImage": "renderScriptImage",
            "renderSegwitImage": "renderSegwitImage",
            "renderStatsImage": "renderStatsImage",
            "reportStatsEnabled": "reportStatsEnabled",
            "shapeOutlineColor": "shapeOutlineColor",
            "shapeShadowColor": "shapeShadowColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dataBlockStatsHistory", [])
        self._defaultattr("graphAverageColor", "#8888ff")
        self._defaultattr("graphBorderColor", "#888888")        # used for graphs for feerates and segwit
        self._defaultattr("graphDataColors", ["#ffff00", "#0000ff", "#00ff00", "#808000", "#ff0000", "#00ffff", "#800000", "#808080", "#008000", "#800080", "#ff00ff", "#008080"])
        self._defaultattr("interval", 300)
        self._defaultattr("renderFeesImage", False)             # time series data disabled by default
        self._defaultattr("renderScriptImage", False)           # time series data disabled by default
        self._defaultattr("renderSegwitImage", False)           # time series data disabled by default
        self._defaultattr("renderStatsImage", True)
        self._defaultattr("reportStatsEnabled", True)
        self._defaultattr("shapeOutlineColor", "#888888")       # used for stats and labels on stats
        self._defaultattr("shapeShadowColor", "#88888888")

        # Initialize
        super().__init__(name="blockstats")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        # only get current block if we're running continuously, 
        # otherwise its expected to have been passed in
        if len(sys.argv) <= 1:
            self.blocknumber = vicariousbitcoin.getcurrentblock()

        self._updateBlockStatsHistory()

    def _loadBlockStatsHistory(self):
        self.dataBlockStatsHistory = []
        fn = self.dataDirectory + "blockstatshistory.json"
        # for loading specific ranges, primarily for testing
        if len(sys.argv) > 1:
            fn = fn.replace(".json","-" + sys.argv[1] + ".json")
        if os.path.exists(fn):
            with open(fn, "r") as f:
                self.dataBlockStatsHistory = json.load(f)

    def _saveBlockStatsHistory(self):
        fn = self.dataDirectory + "blockstatshistory.json"
        # for saving specific ranges, primarily for testing
        # dont want to wipe out general data as its costly to build
        if len(sys.argv) > 1:
            fn = fn.replace(".json","-" + sys.argv[1] + ".json")
        with open(fn, "w") as f:
            json.dump(self.dataBlockStatsHistory, f)

    def _updateBlockStatsHistory(self):
        startblock = self.blocknumber - (self.width-1)
        # load if empty
        if len(self.dataBlockStatsHistory) == 0:
            self._loadBlockStatsHistory()
        # if we have some data
        if len(self.dataBlockStatsHistory) > 0:
            # get highest block so far
            blockheight = self.dataBlockStatsHistory[-1]["height"]
            # adjust startblock
            if blockheight > startblock:
                startblock = blockheight + 1
        eyecandyPoint = 5 if self.renderScriptImage else 50
        # fetch to tip as needed
        startblock = 1 if startblock < 1 and self.blocknumber > 0 else startblock
        if startblock <= self.blocknumber:
            curtime = int(time.time())
            self.log(f"Fetching blockstats history from {startblock} to {self.blocknumber} at {curtime}")
            for i in range(startblock, self.blocknumber+1):
                blockstats = vicariousbitcoin.getblockstats(i)
                if self.renderScriptImage:
                    blockstats["extra"] = vicariousbitcoin.getblockscriptpubkeytypes(i)
                self.dataBlockStatsHistory.append(blockstats)
                # eye candy to logs as this can take time
                if i % eyecandyPoint == 0:
                    if self.renderScriptImage:
                        print('.')
                    curtime = int(time.time())
                    self.log(f"- up to block {i} for {startblock} to {self.blocknumber} range at {curtime}")
                    self._saveBlockStatsHistory()
                else:
                    if self.renderScriptImage:
                        print('.', end='')
            if self.renderScriptImage:
                print('.')
            self.log(f"- done fetching. up to {self.blocknumber}")
        # check if need at beginning
        if len(self.dataBlockStatsHistory) < self.width:
            startblock = self.blocknumber - self.width
            startblock = 1 if startblock < 1 else startblock
            endblock = self.blocknumber if self.blocknumber < 0 else self.dataBlockStatsHistory[0]["height"]
            curtime = int(time.time())
            self.log(f"Fetching blockstats history from {startblock} to {endblock} at {curtime}")
            for i in range(endblock, startblock-1, -1):
                blockstats = vicariousbitcoin.getblockstats(i)
                if self.renderScriptImage:
                    blockstats["extra"] = vicariousbitcoin.getblockscriptpubkeytypes(i)
                self.dataBlockStatsHistory.insert(0, blockstats)
                # eye candy logs
                if i % eyecandyPoint == 0:
                    if self.renderScriptImage:
                        print('.')
                    curtime = int(time.time())
                    self.log(f"- down to block {i} for {startblock} to {endblock} range at {curtime}")
                    self._saveBlockStatsHistory()
                else:
                    if self.renderScriptImage:
                        print('.', end='')
        if self.renderScriptImage:
            print('.')
        # remove early entries no longer needed
        itemstoremove = len(self.dataBlockStatsHistory) - self.width
        if itemstoremove > 0:
            self.dataBlockStatsHistory = self.dataBlockStatsHistory[itemstoremove:]
        # eye candy the range
        firstblock = self.dataBlockStatsHistory[0]["height"]
        lastblock = self.dataBlockStatsHistory[-1]["height"]
        self.log(f"Done fetch blocks. Data for block stats history range {firstblock} - {lastblock}")
        # save current state
        self._saveBlockStatsHistory()

    def _getFieldMinMaxAvgValues(self, thefield):
        if len(self.dataBlockStatsHistory) == 0:
            return -1, -1, -1, -1, -1
        valuemin = None
        valuemax = 0
        valueminx0 = None
        valueminx1 = None
        total = 0
        thefieldparts = thefield.split(".")
        for item in self.dataBlockStatsHistory:
            o = item
            bOK = True
            for thefieldpart in thefieldparts:
                if thefieldpart in o:
                    o = o[thefieldpart]
                else:
                    bOK = False
            v = 0 if not bOK else int(o)
            total += v
            valuemin = v if valuemin is None or v < valuemin else valuemin
            valuemax = v if v > valuemax else valuemax
            valueminx0 = v if valueminx0 is None or v < valueminx0 and v > 0 else valueminx0
            valueminx1 = v if valueminx1 is None or v < valueminx1 and v > 1 else valueminx1
        valueavg = int(float(total) / float(len(self.dataBlockStatsHistory)))
        return valuemin, valuemax, valueavg, valueminx0, valueminx1

    def _reportStats(self):
        blockheight_low, blockheight_high, _, _, _ = self._getFieldMinMaxAvgValues("height")
        feerates_min_low, feerates_min_high, feerates_min_avg, fr_min_x0, fr_min_x1 = self._getFieldMinMaxAvgValues("minfeerate")
        feerates_avg_low, feerates_avg_high, feerates_avg_avg, fr_avg_x0, fr_avg_x1 = self._getFieldMinMaxAvgValues("avgfeerate")
        feerates_max_low, feerates_max_high, feerates_max_avg, fr_max_x0, fr_max_x1 = self._getFieldMinMaxAvgValues("maxfeerate")
        inputs_low, inputs_high, inputs_avg, inputs_x0, inputs_x1 = self._getFieldMinMaxAvgValues("ins")
        outputs_low, outputs_high, outputs_avg, outputs_x0, outputs_x1 = self._getFieldMinMaxAvgValues("outs")
        txs_low, txs_high, txs_avg, txs_x0, txs_x1 = self._getFieldMinMaxAvgValues("txs")
        segwit_low, segwit_high, segwit_avg, segwit_x0, segwit_x1 = self._getFieldMinMaxAvgValues("swtxs")
        taproot_low, taproot_high, taproot_avg, taproot_x0, taproot_x1 = self._getFieldMinMaxAvgValues("extra.vout.witness_v1_taproot")
        self.log(f"   Stats for Blocks  {blockheight_low} - {blockheight_high}")
        self.log(f"=------------------------------------------------------------------------------")
        self.log(f"   Average fee rate: {feerates_avg_low : >5}[{fr_avg_x0 : >5}] - {feerates_avg_high : 7}, avg: {feerates_avg_avg : 5}, x0: {fr_avg_x0 : 5}, x1: {fr_avg_x1 : 5}")
        self.log(f"   Minimum fee rate: {feerates_min_low : >5}[{fr_min_x0 : >5}] - {feerates_min_high : 7}, avg: {feerates_min_avg : 5}, x0: {fr_min_x0 : 5}, x1: {fr_min_x1 : 5}")
        self.log(f"   Maximum fee rate: {feerates_max_low : >5}[{fr_max_x0 : >5}] - {feerates_max_high : 7}, avg: {feerates_max_avg : 5}, x0: {fr_max_x0 : 5}, x1: {fr_max_x1 : 5}")
        self.log(f"             Inputs: {inputs_low : >5}[{inputs_x0 : >5}] - {inputs_high : >7}, avg: {inputs_avg : >5}, x0: {inputs_x0 : >5}, x1: {inputs_x1 : >5}")
        self.log(f"            Outputs: {outputs_low : >5}[{outputs_x0 : >5}] - {outputs_high : >7}, avg: {outputs_avg : >5}, x0: {outputs_x0 : >5}, x1: {outputs_x1 : >5}")
        self.log(f"        Tansactions: {txs_low : >5}[{txs_x1 : >5}] - {txs_high : >7}, avg: {txs_avg : >5}, x0: {txs_x0 : >5}, x1: {txs_x1 : >5}")
        self.log(f" Segwit Tansactions: {segwit_low : >5}[{segwit_x0 : >5}] - {segwit_high : >7}, avg: {segwit_avg : >5}, x0: {segwit_x0 : >5}, x1: {segwit_x1 : >5}")
        if self.renderScriptImage:
            self.log(f"Taproot Tansactions: {taproot_low : >5}[{taproot_x0 : >5}] - {taproot_high : >7}, avg: {taproot_avg : >5}, x0: {taproot_x0 : >5}, x1: {taproot_x1 : >5}")

    def setArtPosition(self):
        """Calculates the Top, Left, Height, and Width of the Stats Block
        
        A calculation of the bounding box area for the art that will be
        generated will be constrained to the largest square that can fit
        within the canvas while allowing for the the header and footer.
        """

        # Act like a singleton, only calculate this the first time
        if hasattr(self, "artHeight"):
            return
        artPadding = 5
        insetTop = self.getInsetTop()
        insetWidth = self.getInsetWidth() - artPadding * 2
        insetHeight = self.getInsetHeight() - artPadding * 2
        self.artHeight = insetHeight if insetWidth > insetHeight else insetWidth
        self.artWidth = self.artHeight
        self.artTop = insetTop + (insetHeight//2) - (self.artHeight//2)
        self.artLeft = (insetWidth//2) - (self.artWidth//2)

    def _getcolorstep(self, s, e, i, m):
        si = int(s,16)
        ei = int(e,16)
        di = ei - si
        ri = si + int(float(di)*float(i)/float(m))
        rh = "{:02x}".format(ri)
        return rh

    def _renderStatsImage(self):

        if len(self.dataBlockStatsHistory) == 0:
            self.log(f"warn: unable to render Stats image. There is no BlockStats in the history")
            self.lastRan = int(time.time())
            return
        self.log(f"Generating image for Stats as of {self.blocknumber}")
        self.headerText = f"Stats for Block {self.blocknumber}"
        self.pageSuffix = None if len(sys.argv) <= 1 else f"{self.blocknumber}"
        super().startImage()
        self.setArtPosition()

        shadowdepth=4
        lwidth=2
        startbyte = 8
        colorchanges = 8        # number of gradients
        gradientwidth = int(self.artWidth / colorchanges)
        blockstats = self.dataBlockStatsHistory[-1]         # last item is most recent
        i = -1
        blockhash = blockstats["blockhash"]
        # determine first start color parts 3 is color band (r,g,b), 2 is for hex of byte
        cstart = ((startbyte+(i*3))*2) 
        rstart = blockhash[cstart:cstart+2]
        gstart = blockhash[cstart+2:cstart+2+2]
        bstart = blockhash[cstart+4:cstart+4+2]
        for i in range(colorchanges):
            # determine ending color parts
            rend = blockhash[cstart+6:cstart+6+2]
            gend = blockhash[cstart+8:cstart+8+2]
            bend = blockhash[cstart+10:cstart+10+2]
            # gradient fill
            startx = self.artLeft + (i * gradientwidth)
            endx = startx + gradientwidth
            for j in range(gradientwidth):
                # calculate gradient stepping per pixel of width
                r = self._getcolorstep(rstart, rend, j, gradientwidth)
                g = self._getcolorstep(gstart, gend, j, gradientwidth)
                b = self._getcolorstep(bstart, bend, j, gradientwidth)
                pointcolor=ImageColor.getrgb(f"#{r}{g}{b}") # build the color
                x = startx + j
                y = self.artTop
                self.draw.line(xy=[(x,y),(x,y+self.artHeight-1)], fill=pointcolor)
            cstart = ((startbyte+(i*3))*2)              # update for next round
            rstart = blockhash[cstart:cstart+2]
            gstart = blockhash[cstart+2:cstart+2+2]
            bstart = blockhash[cstart+4:cstart+4+2]
        # Outline the artwork
        self.draw.rectangle(xy=[(self.artLeft-1,self.artTop-1), \
                                (self.artLeft+self.artWidth,self.artTop+self.artHeight)], \
                                outline=ImageColor.getrgb(self.shapeOutlineColor),width=1)
        # Shadow it (right+bottom)
        self.draw.polygon(xy=[(self.artLeft+self.artWidth+1,self.artTop+shadowdepth),
                        (self.artLeft+self.artWidth+shadowdepth,self.artTop+shadowdepth),
                        (self.artLeft+self.artWidth+shadowdepth,self.artTop+self.artHeight+shadowdepth),
                        (self.artLeft+shadowdepth,self.artTop+self.artHeight+shadowdepth),
                        (self.artLeft+shadowdepth,self.artTop+self.artHeight+1),
                        (self.artLeft+self.artWidth+1,self.artTop+self.artHeight+1)],
                    fill=ImageColor.getrgb(self.shapeShadowColor))
        # Labels
        vicarioustext.drawLabel(self.draw, blockstats["blockhash"], 10, "t", (self.width/2), 75, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        # IOD
        vicarioustext.drawLabel(self.draw, "INPUTS          ", 12, "tl", (self.width/2)-100, 95, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["ins"]), 12, "tr", (self.width/2)-5, 95, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "OUTPUTS         ", 12, "tl", (self.width/2)-100, 111, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["outs"]), 12, "tr", (self.width/2)-5, 111, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "DELTA           ", 12, "tl", (self.width/2)-100, 127, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["utxo_increase"]), 12, "tr", (self.width/2)-5, 127, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        # TX
        vicarioustext.drawLabel(self.draw, "TXS             ", 12, "tl", (self.width/2)+5, 95, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["txs"]), 12, "tr", (self.width/2)+100, 95, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "SEGWIT          ", 12, "tl", (self.width/2)+5, 111, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["swtxs"]), 12, "tr", (self.width/2)+100, 111, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(int(float(blockstats["swtxs"])*100/float(blockstats["txs"])))+"%", 12, "tr", (self.width/2)+100, 127, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        # BLK SIZE, WEIGHT, UTXO SIZE
        vicarioustext.drawLabel(self.draw, "BLK SIZE                                ", 12, "tl", (self.width/2)-100, 147, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["total_size"]), 12, "tr", (self.width/2)+100, 147, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "BLK WEIGHT                           ", 12, "tl", (self.width/2)-100, 163, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["total_weight"]), 12, "tr", (self.width/2)+100, 163, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "UTXO SIZE DELTA                   ", 12, "tl", (self.width/2)-100, 179, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["utxo_size_inc"]), 12, "tr", (self.width/2)+100, 179, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        # MIN / AVG / MAX FEE RATES
        vicarioustext.drawLabel(self.draw, "FEERATES         ", 12, "tl", (self.width/2)-100, 199, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "MIN                ", 12, "tl", (self.width/2)-100, 215, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["minfeerate"]), 12, "tr", (self.width/2)-5, 215, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "AVG                ", 12, "tl", (self.width/2)-100, 231, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["avgfeerate"]), 12, "tr", (self.width/2)-5, 231, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "MAX                ", 12, "tl", (self.width/2)-100, 247, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["maxfeerate"]), 12, "tr", (self.width/2)-5, 247, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "FEES                 ", 12, "tl", (self.width/2)+5, 199, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "MIN            ", 12, "tl", (self.width/2)+5, 215, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["minfee"]), 12, "tr", (self.width/2)+100, 215, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "AVG            ", 12, "tl", (self.width/2)+5, 231, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["avgfee"]), 12, "tr", (self.width/2)+100, 231, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, "MAX            ", 12, "tl", (self.width/2)+5, 247, self.backgroundColor, self.textColor, self.shapeOutlineColor)
        vicarioustext.drawLabel(self.draw, str(blockstats["maxfee"]), 12, "tr", (self.width/2)+100, 247, self.backgroundColor, self.textColor, self.shapeOutlineColor)

        super().finishImage()

    def _renderFeesImage(self):

        if len(self.dataBlockStatsHistory) == 0:
            self.log(f"Unable to render Fees image. There is no BlockStats in the history")
            self.lastRan = int(time.time())
            return
        self.log(f"Generating image for Fee Rates as of {self.blocknumber}")
        blockheight_low = self.dataBlockStatsHistory[0]["height"]
        self.headerText = f"Fee Rates from {blockheight_low} to {self.blocknumber}"
        self.pageSuffix = "feerates" if len(sys.argv) <= 1 else f"feerates-{self.blocknumber}"
        super().startImage()
        chartpad=10
        h3 = (self.getInsetHeight() - (chartpad*2)) // 3
        vicariouschart.drawBarChart(self.draw, 0, self.getInsetTop() + (h3*0), self.width, h3, self.dataBlockStatsHistory, "maxfeerate", True, "Maximum Fee Rate", 144, self.graphDataColors[0], self.graphAverageColor, self.graphBorderColor)
        vicariouschart.drawBarChart(self.draw, 0, self.getInsetTop() + ((h3+chartpad)*1), self.width, h3, self.dataBlockStatsHistory, "avgfeerate", True, "Average Fee Rate", 144, self.graphDataColors[1], self.graphAverageColor, self.graphBorderColor)
        vicariouschart.drawBarChart(self.draw, 0, self.getInsetTop() + ((h3+chartpad)*2), self.width, h3, self.dataBlockStatsHistory, "minfeerate", True, "Minimum Fee Rate", 144, self.graphDataColors[2], self.graphAverageColor, self.graphBorderColor)
        super().finishImage()

    def _renderSegwitImage(self):

        if len(self.dataBlockStatsHistory) == 0:
            self.log(f"Unable to render Segwit image. There is no BlockStats in the history")
            self.lastRan = int(time.time())
            return
        self.log(f"Generating image for Segwit Prevalence as of {self.blocknumber}")
        blockheight_low = self.dataBlockStatsHistory[0]["height"]
        self.headerText = f"Segwit Prevalence from {blockheight_low} to {self.blocknumber}"
        self.pageSuffix = "segwit" if len(sys.argv) <= 1 else f"segwit-{self.blocknumber}"
        super().startImage()
        vicariouschart.drawStackedPercentageBarChart(self.draw, 
                                                     0, self.getInsetTop(), self.width, self.getInsetHeight(),
                                                     self.dataBlockStatsHistory, 
                                                     ("txs", "swtxs"), 
                                                     True, 
                                                     "24 Block (~4 Hour) Intervals", 
                                                     ("NON-SEGWIT TRANSACTIONS", "SEGWIT TRANSACTIONS"),
                                                     24, 
                                                     self.backgroundColor, 
                                                     self.graphDataColors, 
                                                     self.graphBorderColor)
        super().finishImage()

    def _renderScriptImage(self):
        if len(self.dataBlockStatsHistory) == 0:
            self.log(f"Unable to render Scripts images. There is no BlockStats in the history")
            self.lastRan = int(time.time())
            return
        self.log(f"Generating images for Scripts as of {self.blocknumber}")
        blockheight_low = self.dataBlockStatsHistory[0]["height"]

        self.headerText = f"Output Script Types from {blockheight_low} to {self.blocknumber}"
        self.pageSuffix = "scriptouttype" if len(sys.argv) <= 1 else f"scriptouttype-{self.blocknumber}"
        super().startImage()
        vicariouschart.drawStackedPercentageBarChart(self.draw, 
                                                     0, self.getInsetTop(), self.width, self.getInsetHeight(), 
                                                     self.dataBlockStatsHistory, ("",
                                                            "extra.vout.pubkey",
                                                            "extra.vout.pubkeyhash",
                                                            "extra.vout.scripthash",
                                                            "extra.vout.witness_v0_scripthash",
                                                            "extra.vout.witness_v0_keyhash",
                                                            "extra.vout.witness_v1_taproot",
                                                            "extra.vout.nonstandard"), 
                                                     True, 
                                                     "24 Block (~4 Hour) Intervals", ("", 
                                                            "P2PK",
                                                            "P2PKH", 
                                                            "P2SH", 
                                                            "P2WSH", 
                                                            "P2WPKH", 
                                                            "P2TR",
                                                            "NONSTD"),
                                                     24, 
                                                     self.backgroundColor, 
                                                     self.graphDataColors, 
                                                     self.graphBorderColor)
        super().finishImage()

        self.headerText = f"Input Script Types from {blockheight_low} to {self.blocknumber}"
        self.pageSuffix = "scriptintype" if len(sys.argv) <= 1 else f"scriptintype-{self.blocknumber}"
        super().startImage()
        vicariouschart.drawStackedPercentageBarChart(self.draw, 
                                                     0, self.getInsetTop(), self.width, self.getInsetHeight(), 
                                                     self.dataBlockStatsHistory, ("",
                                                            "extra.vin.pubkey",
                                                            "extra.vin.pubkeyhash",
                                                            "extra.vin.scripthash",
                                                            "extra.vin.witness_v0_scripthash",
                                                            "extra.vin.witness_v0_keyhash",
                                                            "extra.vin.witness_v1_taproot",
                                                            "extra.vin.nonstandard"), 
                                                     True, 
                                                     "24 Block (~4 Hour) Intervals", ("", 
                                                            "P2PK",
                                                            "P2PKH", 
                                                            "P2SH", 
                                                            "P2WSH", 
                                                            "P2WPKH", 
                                                            "P2TR",
                                                            "NONSTD"),
                                                     24, 
                                                     self.backgroundColor, 
                                                     self.graphDataColors, 
                                                     self.graphBorderColor)
        super().finishImage()


    def run(self):
        if self.reportStatsEnabled:
            self._reportStats()
        if self.renderStatsImage:
            self._renderStatsImage()
        if self.renderFeesImage:
            self._renderFeesImage()
        if self.renderSegwitImage:
            self._renderSegwitImage()
        if self.renderScriptImage:
            self._renderScriptImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = BlockStatsPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg0 = sys.argv[0]
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces a stat block for a bitcoin block reporting on metrics including inputs, outputs, change to the utxo set, block size and weight, transaction count and portion that is segwit, as well as fee information")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configured defaults")
            print(f"2) Pass the desired block number as an argument as follows")
            print(f"   {arg0} 722231")
            print(f"3) Pass the desired block number, width and height as arguments")
            print(f"   {arg0} 722231 1920 1080")
            exit(0)
        p.blocknumber = int(sys.argv[1])
        p.fetchData()
        if len(sys.argv) > 3:
            p.width = int(sys.argv[2])
            p.height = int(sys.argv[3])
        p.pageSuffix = str(p.blocknumber)
        p.run()
        exit(0)

    # Continuous run
    p.runContinuous()