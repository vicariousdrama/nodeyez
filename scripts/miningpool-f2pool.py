#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

class F2PoolPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new F2Pool panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "account": "accountName",
            "colorBackground": "backgroundColor",
            "colorDataValue": "dataValueColor",
            "colorGraphLineDark": "graphLineDarkColor",
            "colorGraphLineLight": "graphLineLightColor",
            "colorHashDotFill": "hashrateNormalDotFillColor",
            "colorHashDotFillLow": "hashrateLowDotFillColor",
            "colorHashDotFillZero": "hashrateZeroDotFillColor",
            "colorHashDotOutline": "hashrateNormalDotOutlineColor",
            "colorHashDotOutlineLow": "hashrateLowDotOutlineColor",
            "colorHashDotOutlineZero": "hashrateZeroDotOutlineColor",
            "colorMovingAverage": "movingAverageColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "accountName": "accountName",
            "dataValueColor": "dataValueColor",
            "graphLineDarkColor": "graphLineDarkColor",
            "graphLineLightColor": "graphLineLightColor",
            "hashrateLowDotFillColor": "hashrateLowDotFillColor",
            "hashrateLowDotOutlineColor": "hashrateLowDotOutlineColor",
            "hashrateLowThreshold": "hashrateLowThreshold",
            "hashrateNormalDotFillColor": "hashrateNormalDotFillColor",
            "hashrateNormalDotOutlineColor": "hashrateNormalDotOutlineColor",
            "hashrateZeroDotFillColor": "hashrateZeroDotFillColor",
            "hashrateZeroDotOutlineColor": "hashrateZeroDotOutlineColor",
            "movingAverageColor": "movingAverageColor",
            "useTor": "useTor"
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("accountName", "NOT_SET")
        self._defaultattr("dataValueColor", "#4040ff")
        self._defaultattr("graphLineDarkColor", "#606060")
        self._defaultattr("graphLineLightColor", "#a0a0a0")
        self._defaultattr("hashrateLowDotFillColor", "#ffff40")
        self._defaultattr("hashrateLowDotOutlineColor", "#ffff00")
        self._defaultattr("hashrateLowThreshold", 60000000000000)
        self._defaultattr("hashrateNormalDotFillColor", "#4040ff")
        self._defaultattr("hashrateNormalDotOutlineColor", "#0000ff")
        self._defaultattr("hashrateZeroDotFillColor", "#ff4040")
        self._defaultattr("hashrateZeroDotOutlineColor", "#ff0000")
        self._defaultattr("headerText", "F2 Pool Summary")
        self._defaultattr("interval", 600)
        self._defaultattr("movingAverageColor", "#40ff40")
        self._defaultattr("useTor", True)

        # Initialize
        super().__init__(name="miningpool-f2pool")

    def isDependenciesMet(self):

        # Verify accountName set
        if len(self.accountName) == 0 or self.accountName.find("NOT_SET") > -1:
            self.log(f"accountname not configured")
            return False
        return True

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        if not self.isDependenciesMet():
            return

        self.accountinfo = vicariousnetwork.getf2poolaccountinfo(self.useTor, self.accountName)
        self.hashrate = self._getaccounthashrate()
        self.value_last_day = self._getvaluelastday()
        self.value_today = self._getvaluetoday()

    def _getaccounthashrate(self):
        return vicariousbitcoin.gethashratestring(self.accountinfo["hashrate"], "h/s")

    def _getvaluelastday(self):
        return str(int(float(self.accountinfo["value_last_day"]) * 100000000)) + " sats"
    
    def _getvaluetoday(self):
        return str(int(float(self.accountinfo["value_today"]) * 100000000)) + " sats"

    def _gethighesthashrate(self):
        highesthash = self.accountinfo["hashrate"]
        for key in self.accountinfo["hashrate_history"]:
            value = self.accountinfo["hashrate_history"][key]
            currentvalue = float(value)
            if currentvalue > highesthash:
                highesthash = currentvalue
        return highesthash

    def _getlowesthashrate(self):
        lowesthash = self.accountinfo["hashrate"]
        for key in self.accountinfo["hashrate_history"]:
            value = self.accountinfo["hashrate_history"][key]
            currentvalue = float(value)
            if currentvalue < lowesthash:
                lowesthash = currentvalue
        return lowesthash

    def run(self):

        if not self.isDependenciesMet():
            self._markAsRan()
            return

        super().startImage()

        # Hashrate
        hashAreaHeight = self.getInsetHeight() * .40        # was hashheight
        hashAreaLabelSize = int(self.height * (16/320))
        hashAreaValueSize = int(self.height * (24/320))
        earningspad = int(self.height * (24/320))
        vicarioustext.drawcenteredtext(self.draw, "Hashrate",           hashAreaLabelSize, 1*self.width//4, (self.getInsetTop() + (hashAreaHeight//2) - hashAreaValueSize), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, self.hashrate,        hashAreaValueSize, 1*self.width//4, (self.getInsetTop() + (hashAreaHeight//2)), ImageColor.getrgb(self.dataValueColor))
        vicarioustext.drawcenteredtext(self.draw, "Earnings Yesterday", hashAreaLabelSize, 3*self.width//4, (self.getInsetTop() + (hashAreaHeight//2) - hashAreaValueSize - earningspad), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, self.value_last_day,  hashAreaValueSize, 3*self.width//4, (self.getInsetTop() + (hashAreaHeight//2) - earningspad), ImageColor.getrgb(self.dataValueColor))
        vicarioustext.drawcenteredtext(self.draw, "Earnings Today",     hashAreaLabelSize, 3*self.width//4, (self.getInsetTop() + (hashAreaHeight//2) - hashAreaValueSize + earningspad), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, self.value_today,     hashAreaValueSize, 3*self.width//4, (self.getInsetTop() + (hashAreaHeight//2) + earningspad), ImageColor.getrgb(self.dataValueColor))

        # Hashrate History
        highesthashrate = self._gethighesthashrate()
        lowesthashrate = self._getlowesthashrate()
        labelwidth = math.floor(self.width / 5)
        graphedge = 3
        chartLabelSize = int(self.height * (12/320))
        vicarioustext.drawcenteredtext(self.draw, "24 Hour Hashrate", hashAreaLabelSize, self.width//2, (self.getInsetTop() + hashAreaHeight), ImageColor.getrgb(self.textColor))
        charttop = self.getInsetTop() + hashAreaHeight + int(self.height * (12/320))
        chartleft = labelwidth + graphedge
        chartright = self.width - graphedge
        chartbottom = self.getInsetTop() + self.getInsetHeight() - graphedge
        # - chart border
        self.draw.line(xy=[chartleft, charttop, chartleft, chartbottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartleft, chartbottom, chartright, chartbottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartleft, charttop, chartright, charttop],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        self.draw.line(xy=[chartright, charttop, chartright, chartbottom],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - dashed line background
        chart0  = int(math.floor(charttop))
        chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
        chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
        chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
        chart100  = int(math.floor(charttop + ((chartbottom - charttop))))
        for i in range(chartleft, chartright, 10):
            self.draw.line(xy=[i,chart25,i+1,chart25],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart50,i+1,chart50],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart75,i+1,chart75],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - left labels
        hashrate25 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*3)
        hashrate50 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*2)
        hashrate75 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*1)
        vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(highesthashrate, "h/s"), chartLabelSize, labelwidth, chart0,   ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate25, "h/s"),      chartLabelSize, labelwidth, chart25,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate50, "h/s"),      chartLabelSize, labelwidth, chart50,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate75, "h/s"),      chartLabelSize, labelwidth, chart75,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(lowesthashrate, "h/s"),  chartLabelSize, labelwidth, chart100, ImageColor.getrgb(self.textColor))
        # - data plot
        entrynum = 0
        plotbuf=2
        entrycount = len(self.accountinfo["hashrate_history"].keys())
        if entrycount > 0:
            datawidth = ((chartright - chartleft) / entrycount)
            datawidthi = int(math.floor(datawidth))
            for key in self.accountinfo["hashrate_history"]:
                entrynum = entrynum + 1
                datax = chartleft + int(math.floor(entrynum * datawidth))
                datapct = 0
                value = self.accountinfo["hashrate_history"][key]
                if highesthashrate > lowesthashrate:
                    datapct = (value - lowesthashrate)/(highesthashrate - lowesthashrate)
                plottop = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
                dotFillColor = self.hashrateNormalDotFillColor
                dotOutlineColor = self.hashrateNormalDotOutlineColor
                if value < self.hashrateLowThreshold:
                    colorDotFill = self.hashrateLowDotFillColor
                    colorDotOutline = self.hashrateLowDotOutlineColor
                if value == 0:
                    colorDotFill = self.hashrateZeroDotFillColor
                    colorDotOutline = self.hashrateZeroDotOutlineColor
                self.draw.ellipse(xy=[(datax-plotbuf,plottop-plotbuf),(datax+datawidthi+plotbuf,plottop+datawidthi+plotbuf)],fill=ImageColor.getrgb(dotFillColor),outline=ImageColor.getrgb(dotOutlineColor),width=1)
            # moving average line
            entrynum = 0
            ma = [-1,-1,-1]
            olddatax = -1
            olddatay = -1
            for key in self.accountinfo["hashrate_history"]:
                entrynum = entrynum + 1
                value = self.accountinfo["hashrate_history"][key]
                if ma[0] == -1:
                    ma[0] = value
                elif ma[1] == -1:
                    ma[1] = value
                else:
                    ma[2] = value
                    mavg = (ma[0] + ma[1] + ma[2]) / 3
                    datax = chartleft + int(math.floor(entrynum * datawidth))
                    datapct = 0
                    if highesthashrate > lowesthashrate:
                        datapct = (mavg - lowesthashrate)/(highesthashrate - lowesthashrate)
                    datay = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
                    if olddatax != -1:
                        self.draw.line(xy=[(olddatax,olddatay),(datax,datay)],fill=ImageColor.getrgb(self.movingAverageColor),width=3)
                    olddatax = datax
                    olddatay = datay
                    ma[0] = -1 #ma[1]
                    ma[1] = -1 #ma[2]
                    ma[2] = -1

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = F2PoolPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares a summary of F2 Pool hashing and earnings for 24 hours")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            if not p.isDependenciesMet():
                exit(1)
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    