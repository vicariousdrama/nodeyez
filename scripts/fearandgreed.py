#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import glob
import json
import math
import os
import sys
import vicariousnetwork
import vicarioustext

class FearAndGreedPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Fear and Greed panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorAttribution": "attributionColor",
            "colorBackground": "backgroundColor",
            "colorDataValue": "dataValueColor",
            "colorGraphLineDark": "graphLineDarkColor",
            "colorGraphLineLight": "graphLineLightColor",
            "colorMovingAverage": "movingAverageColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "attributionColor": "attributionColor",
            "dataValueColor": "dataValueColor",
            "graphLineDarkColor": "graphLineDarkColor",
            "graphLineLightColor": "graphLineLightColor",
            "movingAverageColor": "movingAverageColor",
            "url": "url",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#aa2222")
        self._defaultattr("dataValueColor", "#ff7f00")
        self._defaultattr("graphLineDarkColor", "#606060")
        self._defaultattr("graphLineLightColor", "#a0a0a0")
        self._defaultattr("headerText", "Fear and Greed Index")
        self._defaultattr("interval", 43200)
        self._defaultattr("movingAverageColor", "#40ff40")
        self._defaultattr("url", "https://api.alternative.me/fng/?limit=0&format=json&date_format=cn")
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="fearandgreed")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.fngHistory = self._getfngHistory()


    def _getnewestfngfile(self, fileDirectory):
        # Restrict the glob pattern to just today
        globpath = fileDirectory + datetime.utcnow().strftime("%Y-%m-%d") + "*.json"
        files = glob.glob(globpath)
        # find the most recently created from the files returned
        newestfile = ""
        if len(files) > 0:
            newestfile = max(files, key=os.path.getctime)
        return newestfile

    def _getfngHistory(self):
        fearAndGreedDataDirectory = f"{self.dataDirectory}fearandgreed/"
        try:
            # Get reference to newest file
            fngfile = self._getnewestfngfile(fearAndGreedDataDirectory)
            print(f"newest fngfile: {fngfile}")
            if len(fngfile) == 0:
                # If dont yet have a file, download and save one
                fngfile = fearAndGreedDataDirectory + datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"
                print(f"Retrieving data from url: {self.url}, and will save to {fngfile}")
                vicariousnetwork.getandsavefile(url=self.url, savetofile=fngfile)
            # Open the file
            print(f"Loading data from {fngfile}")
            with open(fngfile) as f:
                # Load data as JSON
                filedata = json.load(f)
                return filedata
        except Exception as e:
            print(f"Error loading Fear and Greed data: {e}")
            print(f"Using fake data")
        return {"data":[{"value":"50","value_classification":"Neutral","timestamp":"0","time_until_update":"0"}]}

    def run(self):

        super().startImage()

        infoHeight = self.getInsetHeight() * .3
        chartHeight = self.getInsetHeight() * .7
        fngValueSize = int(self.height * 48/320)
        fngLabelSize = int(self.height * 20/320)
        labelSize = int(self.height * 12/320)
        attributionSize = int(self.height * 14/320)
        # FNG History
        labelWidth = 40
        graphBuffer = 3
        chartTop = self.getInsetTop() + self.getInsetHeight() - chartHeight + 12
        chartLeft = labelWidth + graphBuffer
        chartRight = self.width - graphBuffer
        chartBottom = self.getInsetTop() + self.getInsetHeight() - graphBuffer
        # - chart border
        self.draw.line(xy=[chartLeft, chartTop, chartLeft, chartBottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartLeft, chartBottom, chartRight, chartBottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartLeft, chartTop, chartRight, chartTop],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        self.draw.line(xy=[chartRight, chartTop, chartRight, chartBottom],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - dashed line background
        chart100 = int(math.floor(chartTop))
        chart80  = int(math.floor(chartTop + ((chartBottom - chartTop)/5*1)))
        chart60  = int(math.floor(chartTop + ((chartBottom - chartTop)/5*2)))
        chart40  = int(math.floor(chartTop + ((chartBottom - chartTop)/5*3)))
        chart20  = int(math.floor(chartTop + ((chartBottom - chartTop)/5*4)))
        chart0   = int(math.floor(chartTop + ((chartBottom - chartTop))))
        for i in range(chartLeft, chartRight, 10):
            self.draw.line(xy=[i,chart20,i+1,chart20],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart40,i+1,chart40],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart60,i+1,chart60],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart80,i+1,chart80],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - left labels
        vicarioustext.drawrighttext(self.draw, "100%", labelSize, labelWidth, chart100, ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, "80%",  labelSize, labelWidth, chart80,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, "60%",  labelSize, labelWidth, chart60,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, "40%",  labelSize, labelWidth, chart40,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, "20%",  labelSize, labelWidth, chart20,  ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, "0%",   labelSize, labelWidth, chart0,   ImageColor.getrgb(self.textColor))
        # - data plot
        highestPercent = 0.0
        highestXPos = 0
        highestYPos = 0
        entryNum = 0
        plotBuf = 1
        xBuf = 0
        yBuf = 0
        fngLength = len(self.fngHistory["data"])
        oldMovingAverageXPos = -1
        oldMovingAverageYPos = -1
        oldDateLabel = ""
        for entry in self.fngHistory["data"]:
            # current data point
            entryNum = entryNum + 1
            fngPercent = entry["value"]
            xPos = chartRight - (entryNum * plotBuf)
            yPos = chartBottom - int(math.floor((chartBottom-chartTop) / 100.0 * float(fngPercent)))
            if float(fngPercent) > highestPercent:
                highestPercent = float(fngPercent)
                highestXPos = xPos
                highestYPos = yPos
            if ((xBuf+xPos-plotBuf) <= chartLeft):
                break
            self.draw.ellipse(xy=[(xBuf+xPos-plotBuf,yBuf+yPos-plotBuf),(xBuf+xPos+plotBuf,yBuf+yPos+plotBuf)],fill=ImageColor.getrgb(self.dataValueColor),outline=ImageColor.getrgb(self.dataValueColor),width=1)
            # tick mark label
            fngTimestamp = entry["timestamp"]
            dateLabel = oldDateLabel
            if "-" in fngTimestamp:
                dateYear = fngTimestamp[0:4]
                dateMonth = fngTimestamp[5:7]
                dateDay = fngTimestamp[8:10]
                if int(dateMonth) % 3 == 1:
                    if int(dateDay) == 1:
                        dateLabel = fngTimestamp[0:7]
            else:
                dateObject = datetime.fromtimestamp(int(fngTimestamp))
                if ((dateObject.month % 3) == 1):
                    if (dateObject.day == 1):
                        dateLabel = str(dateObject.year) + "-" + str(dateObject.month).rjust(2,'0')
            if oldDateLabel != dateLabel:
                lw,lh,lf = vicarioustext.gettextdimensions(self.draw, dateLabel, labelSize, False)
                self.draw.line(xy=[xPos,chartTop,xPos,chartBottom],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
                if (xPos + graphBuffer + lw < chartRight):
                    vicarioustext.drawbottomlefttext(self.draw, dateLabel, labelSize, xPos + 1, chartBottom, ImageColor.getrgb(self.graphLineLightColor), False)
                oldDateLabel = dateLabel
            # moving average calculation (14 points = 7 day)
            movingAverageSize = 14
            movingAverageTotal = 0
            for movingAverageEntry in range(movingAverageSize):
                movingAverageIndex = entryNum - 1 + movingAverageEntry
                if (movingAverageIndex >= 0) and (movingAverageIndex < fngLength):
                    movingAverageEntryValue = self.fngHistory["data"][movingAverageIndex]["value"]
                    movingAverageEntryPercent = int(movingAverageEntryValue)
                    movingAverageTotal = movingAverageTotal + movingAverageEntryPercent
            movingAveragePercent = float(movingAverageTotal) / float(movingAverageSize)
            yPos = chartBottom - int(math.floor((chartBottom-chartTop) / 100.0 * movingAveragePercent))
            if oldMovingAverageXPos != -1:
                self.draw.line(xy=[(xPos,yPos),(oldMovingAverageXPos,oldMovingAverageYPos)],fill=ImageColor.getrgb(self.movingAverageColor),width=2)
            oldMovingAverageXPos = xPos
            oldMovingAverageYPos = yPos
        # Info
        currentvalue = "50"
        currentlabel = "Neutral"
        if fngLength > 0:
            currentvalue = self.fngHistory["data"][0]["value"]
            currentlabel = self.fngHistory["data"][0]["value_classification"]
            # indicate highest alue
            if highestXPos > float(self.width/2):
                # anchor bottom right
                self.draw.rectangle([(highestXPos-((labelSize*4)+2),highestYPos-(labelSize*1.5)-2),(highestXPos,highestYPos-2)], outline=ImageColor.getrgb(self.graphLineLightColor), fill=ImageColor.getrgb(self.backgroundColor))
                vicarioustext.drawcenteredtext(self.draw, str(int(highestPercent)), labelSize, highestXPos-((labelSize*2)+1), highestYPos-(labelSize-1), ImageColor.getrgb(self.dataValueColor))
            else:
                # anchor bottom left
                self.draw.rectangle([(highestXPos+((labelSize*4)+2),highestYPos-(labelSize*1.5)-2),(highestXPos,highestYPos-2)], outline=ImageColor.getrgb(self.graphLineLightColor), fill=ImageColor.getrgb(self.backgroundColor))
                vicarioustext.drawcenteredtext(self.draw, str(int(highestPercent)), labelSize, highestXPos+((labelSize*2)+1), highestYPos-(labelSize-1), ImageColor.getrgb(self.dataValueColor))
        print(f"Current Value: {currentvalue} - {currentlabel}")
        vicarioustext.drawcenteredtext(self.draw, currentvalue, fngValueSize, self.width//2, (self.getInsetTop() + (1*infoHeight//3)), ImageColor.getrgb(self.dataValueColor), True)
        vicarioustext.drawcenteredtext(self.draw, currentlabel, fngLabelSize, self.width//2, (self.getInsetTop() + (2*infoHeight//3)), ImageColor.getrgb(self.dataValueColor), True)
        # Attribution
        attributionLine = "Data from alternative.me"
        vicarioustext.drawbottomlefttext(self.draw, attributionLine, attributionSize, 0, self.height, ImageColor.getrgb(self.attributionColor))


        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = FearAndGreedPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for Fear and Greed charting")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    