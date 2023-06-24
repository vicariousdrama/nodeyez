#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import sys
import vicarioustext

class UTCClockPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new UTC Clock panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextDate": "dateTextColor",
            "colorTextDayOfWeek": "dayOfWeekTextColor",
            "colorTextTime": "timeTextColor",
            "sleepInterval": "interval",
            # panel specific key names
            "dateTextColor": "dateTextColor",
            "dayOfWeekTextColor": "dayOfWeekTextColor",
            "timeTextColor": "timeTextColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dateTextColor", "#f1c232")
        self._defaultattr("dayOfWeekTextColor", "#e69138")
        self._defaultattr("footerEnabled", False)
        self._defaultattr("headerEnabled", False)
        self._defaultattr("interval", 30)
        self._defaultattr("timeTextColor", "#6aa84f")
        self._defaultattr("watermarkEnabled", False)

        # Initialize
        super().__init__(name="utcclock")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.now = datetime.utcnow()

    def run(self):

        super().startImage()

        dayofweek = self.now.strftime("%A")
        fs,_,_ = vicarioustext.getmaxfontsize(self.draw, dayofweek, self.width, self.height//3, True)
        vicarioustext.drawcenteredtext(self.draw, dayofweek, fs, self.width//2, self.height*1//6, ImageColor.getrgb(self.dayOfWeekTextColor))

        date = self.now.strftime("%d %b %Y")
        fs,_,_ = vicarioustext.getmaxfontsize(self.draw, date, self.width, self.height//3, True)
        vicarioustext.drawcenteredtext(self.draw, date, fs, self.width//2, self.height*3//6, ImageColor.getrgb(self.dateTextColor))

        time = self.now.strftime("%H:%M:%S")
        fs,_,_ = vicarioustext.getmaxfontsize(self.draw, time, self.width, self.height//3, True)
        vicarioustext.drawcenteredtext(self.draw, time, fs, self.width//2, self.height*5//6, ImageColor.getrgb(self.timeTextColor))

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = UTCClockPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a simple output of the date and time in UTC and weekday")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()