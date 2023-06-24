#! /usr/bin/env python3
from LuxorLabs.luxor import API
from PIL import ImageColor
from calendar import monthrange
from datetime import datetime
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousbitcoin
import vicarioustext

class LuxorPoolPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LuxorPool panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
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
            "apikey": "apikey",
            "dataValueColor": "dataValueColor",
            "graphLineDarkColor": "graphLineDarkColor",
            "graphLineLightColor": "graphLineLightColor",
            "hashrateLowDotFillColor": "hashrateLowDotFillColor",
            "hashrateLowDotOutlineColor": "hashrateLowDotOutlineColor",
            "hashrateLowThreshold": "hashrateLowThreshold",
            "hashrateNormalDotFillColor": "hashrateNormalDotFillColor",
            "hashrateNormalDotOutlineColor": "hashrateNormalDotOutlineColor",
            "hashrateTarget": "hashrateTarget",
            "hashrateZeroDotFillColor": "hashrateZeroDotFillColor",
            "hashrateZeroDotOutlineColor": "hashrateZeroDotOutlineColor",
            "movingAverageColor": "movingAverageColor",
            "subheadingText": "subheadingText",
            "username": "username",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("apikey", "NOT_SET")
        self._defaultattr("dataValueColor", "#4040ff")
        self._defaultattr("graphLineDarkColor", "#606060")
        self._defaultattr("graphLineLightColor", "#a0a0a0")
        self._defaultattr("hashrateLowDotFillColor", "#ffff40")
        self._defaultattr("hashrateLowDotOutlineColor", "#ffff00")
        self._defaultattr("hashrateLowThreshold", 90000000000000)
        self._defaultattr("hashrateNormalDotFillColor", "#4040ff")
        self._defaultattr("hashrateNormalDotOutlineColor", "#0000ff")
        self._defaultattr("hashrateTarget", 110000000000000)
        self._defaultattr("hashrateZeroDotFillColor", "#ff4040")
        self._defaultattr("hashrateZeroDotOutlineColor", "#ff0000")
        self._defaultattr("headerText", "Luxor Pool Summary")
        self._defaultattr("interval", 86400)
        self._defaultattr("movingAverageColor", "#40ff40")
        self._defaultattr("subheadingText", "S19 Pro 110TH")
        self._defaultattr("useTor", True)
        self._defaultattr("username", "NOT_SET")

        # Initialize
        super().__init__(name="miningpool-luxorpool")

    def isDependenciesMet(self):

        # Verify apikey set
        if len(self.apikey) == 0 or self.apikey.find("NOT_SET") > -1:
            self.log(f"apikey not configured")
            return False
        # Verify username name
        if len(self.username) == 0 or self.username.find("NOT_SET") > -1:
            self.log(f"username not configured")
            return False
        return True

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        if not self.isDependenciesMet():
            return

        LUXORAPI = API(host = 'https://api.beta.luxor.tech/graphql', method='POST', org='luxor', key=self.apikey)
        resp = LUXORAPI.get_hashrate_score_history(self.username,'BTC',100)
        self.hashrateHistory = resp['data']['getHashrateScoreHistory']['nodes']

    def _getHighestHashrateForDatePrefix(self, datePrefix):
        highest = 0
        for entry in self.hashrateHistory:
            entryPrefix = entry["date"][:7]
            if entryPrefix != datePrefix: continue
            value = float(entry["hashrate"])
            if value > highest: highest = value
        return highest

    def _getUniqueMonths(self):
        uniqueMonths = []
        datePrefix = ""
        for entry in self.hashrateHistory:
            entryPrefix = entry["date"][:7]
            if entryPrefix != datePrefix:
                datePrefix = entryPrefix
                uniqueMonths.append(datePrefix)
        return uniqueMonths

    def run(self):

        if not self.isDependenciesMet():
            self._markAsRan()
            return

        uniqueMonths = self._getUniqueMonths()

        labelWidth = self.width // 5
        graphEdge = int(self.width * 3/480)

        for uniqueMonth in uniqueMonths:

            month = int(uniqueMonth[5:7])
            year = int(uniqueMonth[:4])
            dateObject = datetime.strptime(str(month), "%m")
            monthName = dateObject.strftime("%B")
            self.pageSuffix = uniqueMonth
            super().startImage()

            # Info area
            infoHeight = self.getInsetHeight() * .3
            fontSize = int(self.height * 16/320)
            subheaderCenterY = self.getInsetTop() + (fontSize // 2)
            vicarioustext.drawcenteredtext(self.draw, self.subheadingText, fontSize, self.width//2, subheaderCenterY, ImageColor.getrgb(self.textColor), False)
            vicarioustext.drawcenteredtext(self.draw, f"Daily Hashrate Average for {monthName} {year}", fontSize, self.width//2, self.getInsetTop() + infoHeight, ImageColor.getrgb(self.textColor))

            # Hashrate History
            highestHashrate = self._getHighestHashrateForDatePrefix(uniqueMonth)
            lowestHashrate = 0

            # Chart area
            chartPadding = int(self.height * 12/320)
            chartTop = self.getInsetTop() + infoHeight + chartPadding
            chartLeft = labelWidth + graphEdge
            chartRight = self.width - graphEdge
            chartBottom = self.getInsetTop() + self.getInsetHeight() - graphEdge
            # - chart border
            self.draw.line(xy=[chartLeft, chartTop, chartLeft, chartBottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
            self.draw.line(xy=[chartLeft, chartBottom, chartRight, chartBottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
            self.draw.line(xy=[chartLeft, chartTop, chartRight, chartTop],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[chartRight, chartTop, chartRight, chartBottom],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            # - dashed line background
            chart0  = chartTop//1
            chart25 = chartTop//1 + (chartBottom-chartTop)//4
            chart50 = chartTop//1 + (chartBottom-chartTop)//2
            chart75 = chartTop//1 + (chartBottom-chartTop)//4*3
            chart100 = chartTop//1 + (chartBottom-chartTop)
            for i in range(chartLeft, chartRight, 10):
                self.draw.line(xy=[i,chart25,i+1,chart25],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
                self.draw.line(xy=[i,chart50,i+1,chart50],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
                self.draw.line(xy=[i,chart75,i+1,chart75],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            # - left labels
            fontSize = int(self.height * 12 /320)
            hashrate25 = lowestHashrate + ((highestHashrate - lowestHashrate)/4*3)
            hashrate50 = lowestHashrate + ((highestHashrate - lowestHashrate)/4*2)
            hashrate75 = lowestHashrate + ((highestHashrate - lowestHashrate)/4*1)            
            vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(highestHashrate, "h/s"), fontSize, labelWidth, chart0, ImageColor.getrgb(self.textColor))
            vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate25, "h/s"), fontSize, labelWidth, chart25, ImageColor.getrgb(self.textColor))
            vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate50, "h/s"), fontSize, labelWidth, chart50, ImageColor.getrgb(self.textColor))
            vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(hashrate75, "h/s"), fontSize, labelWidth, chart75, ImageColor.getrgb(self.textColor))
            vicarioustext.drawrighttext(self.draw, vicariousbitcoin.gethashratestring(lowestHashrate, "h/s"), fontSize, labelWidth, chart100, ImageColor.getrgb(self.textColor))
            # - data plot
            totalvalue=0
            entrynum=0
            plotbuf=2
            xbuf=-8
            ybuf=-2
            daycount = monthrange(year, month)[1]
            dataWidth = ((chartRight - chartLeft) / daycount)
            dataWidthI = 3 # int(math.floor(datawidth))
            dayseen=[False]*daycount
            for entry in self.hashrateHistory:
                if entry["date"][:7] == uniqueMonth:
                    daynum = int(entry["date"][8:10])
                    dayseen[daynum-1]=True
                    datax = chartLeft + int(math.floor(daynum * dataWidth))
                    datapct = 0
                    value = float(entry["hashrate"])
                    totalvalue += value
                    if highestHashrate > lowestHashrate:
                        datapct = (value - lowestHashrate)/(highestHashrate - lowestHashrate)
                    plottop = chartBottom - int(math.floor((chartBottom-chartTop)*datapct))
                    dotFillColor = self.hashrateNormalDotFillColor
                    dotOutlineColor = self.hashrateNormalDotOutlineColor
                    if value < self.hashrateLowThreshold:
                        dotFillColor = self.hashrateLowDotFillColor
                        dotOutlineColor = self.hashrateLowDotOutlineColor
                    if value == 0:
                        dotFillColor = self.hashrateZeroDotFillColor
                        dotOutlineColor = self.hashrateZeroDotOutlineColor
                    self.draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+dataWidthI+plotbuf,ybuf+plottop+dataWidthI+plotbuf)],fill=ImageColor.getrgb(dotFillColor),outline=ImageColor.getrgb(dotOutlineColor),width=1)
            # plot missing days
            for daynum in range(len(dayseen)):
                if dayseen[daynum] == False:
                    themissingdate = datetime(year, month, daynum+1)
                    if themissingdate.timestamp() < datetime.today().timestamp():
                        datax = chartLeft + int(math.floor((daynum+1) * dataWidth))
                        datapct = 0
                        plottop = chartBottom - int(math.floor((chartBottom-chartTop)*datapct))
                        dotFillColor = self.hashrateZeroDotFillColor
                        dotOutlineColor = self.hashrateZeroDotOutlineColor
                        self.draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+dataWidthI+plotbuf,ybuf+plottop+dataWidthI+plotbuf)],fill=ImageColor.getrgb(dotFillColor),outline=ImageColor.getrgb(dotOutlineColor),width=1)
                    else:
                        # set daycount to today to allow average and result percent to calculate properly
                        daycount = int(datetime.now().strftime("%d"))

            # Expected Total, and Percentage thereof reported in the info area
            totalexpected = daycount * self.hashrateTarget
            resultpercent = totalvalue / totalexpected
            averageHashrate = int(totalvalue / daycount)
            #print(f"{month_name} {year} expected {totalexpected} got {totalvalue}, {resultpercent}")
            hashTarget = vicariousbitcoin.gethashratestring(self.hashrateTarget, "h/s")
            hashAverage = vicariousbitcoin.gethashratestring(averageHashrate, "h/s")
            fontSize = int(self.height * 16/320)
            centerY = self.getInsetTop() + int(self.height * 32/320)
            vicarioustext.drawcenteredtext(self.draw, "Target", fontSize, int(self.width/6), centerY, ImageColor.getrgb(self.hashrateNormalDotFillColor))
            vicarioustext.drawcenteredtext(self.draw, "Average", fontSize, int(self.width/2), centerY, ImageColor.getrgb(self.hashrateNormalDotFillColor))
            vicarioustext.drawcenteredtext(self.draw, "Uptime", fontSize, int(self.width/6)*5, centerY, ImageColor.getrgb(self.hashrateNormalDotFillColor))
            fontSize = int(self.height * 18/320)
            centerY = self.getInsetTop() + int(self.height * 52/320)
            vicarioustext.drawcenteredtext(self.draw, hashTarget, fontSize, int(self.width/6), centerY, ImageColor.getrgb(self.textColor))
            vicarioustext.drawcenteredtext(self.draw, hashAverage, fontSize, int(self.width/2), centerY, ImageColor.getrgb(self.textColor))
            vicarioustext.drawcenteredtext(self.draw, f"{int(resultpercent*100)}%", fontSize, int(self.width/6)*5, centerY, ImageColor.getrgb(self.textColor))

            super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LuxorPoolPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for Luxor Mining Hashrate for each month in the dataset")
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