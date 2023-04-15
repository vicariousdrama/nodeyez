#! /usr/bin/env python3
from PIL import ImageColor
from bs4 import BeautifulSoup
from vicariouspanel import NodeyezPanel
import sys
import vicariousnetwork
import vicarioustext

class CompassMiningStatusPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Compass Mining Status panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorCritical": "criticalBackgroundColor",
            "colorCriticalText": "criticalTextColor",
            "colorGood": "goodBackgroundColor",
            "colorGoodText": "goodTextColor",
            "colorMaintenance": "maintenanceBackgroundColor",
            "colorMaintenanceText": "maintenanceTextColor",
            "colorMajor": "majorBackgroundColor",
            "colorMajorText": "majorTextColor",
            "colorMinor": "minorBackgroundColor",
            "colorMinorText": "minorTextColor",
            "colorNone": "noneBackgroundColor",
            "colorNoneText": "noneTextColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            "statusurl": "statusURL",
            # panel specific key names
            "criticalBackgroundColor": "criticalBackgroundColor",
            "criticalTextColor": "criticalTextColor",
            "goodBackgroundColor": "goodBackgroundColor",
            "goodTextColor": "goodTextColor",
            "maintenanceBackgroundColor": "maintenanceBackgroundColor",
            "maintenanceTextColor": "maintenanceTextColor",
            "majorBackgroundColor": "majorBackgroundColor",
            "majorTextColor": "majorTextColor",
            "minorBackgroundColor": "minorBackgroundColor",
            "minorTextColor": "minorTextColor",
            "noneBackgroundColor": "noneBackgroundColor",
            "noneTextColor": "noneTextColor",
            "statusURL": "statusURL",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerText", "Compass Mining Facility Status")
        self._defaultattr("interval", 900)
        self._defaultattr("criticalBackgroundColor", "#ff7a00")
        self._defaultattr("criticalTextColor", "#ffffff")
        self._defaultattr("goodBackgroundColor", "#000000")
        self._defaultattr("goodTextColor", "#40ff40")
        self._defaultattr("maintenanceBackgroundColor", "#2020ff")
        self._defaultattr("maintenanceTextColor", "#ffffff")
        self._defaultattr("majorBackgroundColor", "#ff2020")
        self._defaultattr("majorTextColor", "#ffffff")
        self._defaultattr("minorBackgroundColor", "#2020ff")
        self._defaultattr("minorTextColor", "#ffffff")
        self._defaultattr("noneBackgroundColor", "#333333")
        self._defaultattr("noneTextColor", "#ffffff")
        self._defaultattr("statusPage", "")
        self._defaultattr("statusURL", "https://status.compassmining.io/")
        self._defaultattr("useTor", True)

        # Initialize
        super().__init__(name="compassminingstatus")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        # retrieve the latest status
        statusPage = vicariousnetwork.getpage(self.useTor, self.statusURL, "", None)
        if len(statusPage) > 0:
            self.statusPage = statusPage


    def run(self):

        super().startImage()

        # init beautiful soup with the most current status page
        soup = BeautifulSoup(self.statusPage, 'html.parser')
        incidentPriorities = ["major", "critical", "maintenance", "minor", "none"]
        incidentCount = 0
        incidentHeight = self.height // 10
        for incidentType in incidentPriorities:
            incidentClass = f"impact-{incidentType}"
            incidentBackgroundColor = ImageColor.getrgb(self.__getattribute__(f"{incidentType}BackgroundColor"))
            incidentTextColor = ImageColor.getrgb(self.__getattribute__(f"{incidentType}TextColor"))
            incidents = soup.find_all(class_=incidentClass)
            for incident in incidents:
                titleobj = incident.find(class_="actual-title")
                if titleobj is None:
                    continue
                text = titleobj.get_text()
                incidentCount += 1
                # background
                self.draw.rectangle(xy=[0,self.getInsetTop()+((incidentCount-1)*incidentHeight)+1,self.width,self.getInsetTop()+int((incidentCount)*incidentHeight)-1], fill=incidentBackgroundColor)
                # size text to fit
                maxFontSize = incidentHeight
                minFontSize = 8
                fs, sw, sh = vicarioustext.getmaxfontsize(self.draw, text, self.width, self.height, True, maxFontSize, minFontSize)
                textFits = fs >= minFontSize
                if textFits:
                    # center
                    vicarioustext.drawcenteredtext(self.draw, text, fs, self.width//2, self.getInsetTop() + int((incidentCount-1)*incidentHeight) + incidentHeight//2, incidentTextColor, True)
                else:
                    # left align
                    vicarioustext.drawlefttext(self.draw, text, fs, 0, self.getInsetTop() + int((incidentCount-1)*incidentHeight) + incidentHeight//2, incidentTextColor, True)

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = CompassMiningStatusPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the Compass Mining status page and prepares a summary image")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()    