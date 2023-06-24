#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import glob
import json
import os
import random
import sys
import vicariouslookup
import vicariousnetwork
import vicarioustext

class GasPricePanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Gas Price panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "colorTextGas": "gasTextColor",
            "colorTextLocation": "locationTextColor",
            "colorTextPrice": "priceTextColor",
            "dataCountry": "activeCountry",
            "dataState": "activeState",
            "randomCountry": "randomCountryEnabled",
            "randomState": "randomStateEnabled",
            "sleepInterval": "interval",
            # panel specific key names
            "activeCountry": "activeCountry",
            "activeState": "activeState",
            "gasTextColor": "gasTextColor",
            "locationTextColor": "locationTextColor",
            "priceTextColor": "priceTextColor",
            "randomCountryEnabled": "randomCountryEnabled",
            "randomStateEnabled": "randomStateEnabled",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("activeCountry", "USA")
        self._defaultattr("activeState", "California")
        self._defaultattr("attributionColor", "#40ff40")
        self._defaultattr("backgroundColor", "#000060")
        self._defaultattr("gasData", {"result":[{"currency":"usd","name":"California","gasoline":"5.702"}]})
        self._defaultattr("gasTextColor", "#e69138")
        self._defaultattr("headerText", "Gas Prices")
        self._defaultattr("interval", 3600)
        self._defaultattr("locationTextColor", "#f1c232")
        self._defaultattr("priceTextColor", "#6aa84f")
        self._defaultattr("randomCountryEnabled", True)
        self._defaultattr("randomStateEnabled", True)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="gasprice")

    def getDataDirectory(self):
        if self.activeCountry == "USA":
            return f"{self.dataDirectory}collectapi/gasprice/allusaprice/"
        if self.activeCountry == "CAN":
            return f"{self.dataDirectory}collectapi/gasprice/canada/"
        # default
        return f"{self.dataDirectory}collectapi/gasprice/allusaprice/"

    def getNewestFile(self):
        newestFile = None
        gasfileDirectory = self.getDataDirectory()
        files = glob.glob(gasfileDirectory + "*.json")
        if len(files) > 0:
            newestFile = max(files, key=os.path.getctime)
        return newestFile

    def getItemIndexForState(self, name):
        itemIndex = -1
        if self.gasData is None:
            return itemIndex
        for item in self.gasData["result"]:
            itemIndex += 1
            if item["name"] == name:
                break
        return itemIndex

    def getItemInfo(self, itemIndex):
        if self.gasData is None:
            return "Unknown", "usd", "99.99"
        if itemIndex > len(self.gasData["result"]) - 1:
            return "Unknown", "usd", "99.99"
        o = self.gasData["result"][itemIndex]
        return o["name"], o["currency"], o["gasoline"]

    def blockclockReport(self):
        baseapi=f"http://{self.blockclockAddress}/api/"
        # a make the value have 5 digits total pad out right side
        rprice = str(self.gasPrice)
        while len(rprice) < 6:
            rprice = rprice + "9"
        # send basic price info
        vicariousnetwork.getblockclockapicall(baseapi + "show/number/" + rprice + "?sym=$&pair=GAS/", self.blockclockPassword)
        voltype = "GAL" if self.activeCountry == "USA" else "LITER"
        abbrev = vicariouslookup.USAStateAbbreviation[self.gasName] if self.activeCountry == "USA" else vicariouslookup.CANProvinceAbbreviation[self.gasName]
        # b slot 5 is currency and volume
        vicariousnetwork.getblockclockapicall(baseapi + "ou_text/5/USD/" + voltype, self.blockclockPassword)
        # c slot 6 is location
        vicariousnetwork.getblockclockapicall(baseapi + "ou_text/6/" + abbrev + "/" + self.activeCountry, self.blockclockPassword)

    def isDependenciesMet(self):
        # Must have data directories
        dataDirectory = self.getDataDirectory()
        if not os.path.exists(dataDirectory):
            self.log(f"data directory does not exist {dataDirectory}")
            return False
        # Must have a file
        if self.getNewestFile() is None:
            self.log(f"no files exist in data directory {dataDirectory}")
            return False
        # Must have gas data
        if not self.isGasDataValid():
            self.log(f"current gas data is not valid")
            return False
        return True

    def isGasDataValid(self):
        if self.gasData is None:
            self.log(f"no gas data available to process")
            return False
        if type(self.gasData) is not dict:
            self.log(f"gas data is not in expected format")
            return False
        if "result" not in self.gasData:
            self.log(f"gas data has no result")
            return False
        if len(self.gasData["result"]) == 0:
            self.log(f"gas data has no result")
            return False
        return True


    def fetchData(self):
        """Fetches all the data needed for this panel"""
        if self.randomCountryEnabled:
            countryIndex = int(random.random() * 2)
            self.activeCountry = "USA" if countryIndex == 0 else "CAN"
        newestFile = self.getNewestFile()
        if newestFile is not None:
            with open(newestFile) as f:
                self.gasData = json.load(f)
        if not self.isGasDataValid():
            return
        itemCount = len(self.gasData["result"])
        itemIndex = self.getItemIndexForState(self.activeState)
        if itemIndex == -1 and not self.randomCountryEnabled and not self.randomStateEnabled:
            self.log(f"Could not find state or province named {self.activeState} in selected gas data file. Choosing randomly")
        if self.randomCountryEnabled or self.randomStateEnabled or itemIndex == -1:
            itemIndex = int(random.random() * itemCount)
        self.gasName, self.gasCurrency, self.gasPrice = self.getItemInfo(itemIndex)

    def run(self):
        if not self.isDependenciesMet():
            self._markAsRan()
            return

        super().startImage()
        centerX = self.width // 2
        centerY = self.height // 2
        valueOffset = int(self.height*48/320)
        # location
        locationSize = int(self.height*64/320)
        fs, _, _ = vicarioustext.getmaxfontsize(self.draw, self.gasName, self.width, locationSize, True, locationSize)
        vicarioustext.drawcenteredtext(self.draw, self.gasName, fs, centerX, centerY-valueOffset, ImageColor.getrgb(self.locationTextColor))
        # price
        priceUnit = "gallon" if self.activeCountry == "USA" else "liter"
        priceLabel = f"${self.gasPrice}/{priceUnit}"
        priceSize = int(self.height*72/320)
        fs, _, _ = vicarioustext.getmaxfontsize(self.draw, priceLabel, self.width, priceSize, True, priceSize)
        vicarioustext.drawcenteredtext(self.draw, priceLabel, fs, centerX, centerY+valueOffset, ImageColor.getrgb(self.priceTextColor))
        # attribution
        attributionSize = int(self.height*14/320)
        vicarioustext.drawbottomlefttext(self.draw, "Data from CollectAPI", attributionSize, 0, self.height, ImageColor.getrgb(self.attributionColor))
        super().finishImage()

        if self.blockclockEnabled:
            self.blockclockReport()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = GasPricePanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a simple output of the average price of gas for a state or privince in the US or Canada")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    