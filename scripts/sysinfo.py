#! /usr/bin/env python3
from vicariousicon import VicariousIcons
from vicariouspanel import NodeyezPanel
import sys
import vicariousstat

class SysInfoPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new System Info panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "sleepInterval": "interval",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerEnabled", False)
        self._defaultattr("interval", 60)
        self._defaultattr("watermarkEnabled", False)

        # Initialize
        super().__init__(name="sysinfo")
        self.icons = VicariousIcons()
        self.icons.thermometerWarnLevel = vicariousstat.getcputempwarnlevel()
        self.icons.thermometerDangerLevel = vicariousstat.getcputempdangerlevel()

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.cpuLoad = vicariousstat.getload()
        self.cpuTemp = vicariousstat.getcputemp()
        self.drive1Info = vicariousstat.getdrive1info()
        self.drive2Info = vicariousstat.getdrive2info()
        self.memoryInfo = vicariousstat.getmemoryinfo("Mem")
        self.swapInfo = vicariousstat.getmemoryinfo("Swap")

    def run(self):

        super().startImage()
        self.icons.draw = self.draw
        w = self.width // 3
        h = self.height // 2
        # Row 1
        x = 0
        y = 0
        # Temp
        self.icons.drawThermometer(x, y, w, h, self.cpuTemp)
        x += w
        # Drive 1
        self.icons.drawDrive(x, y, w, h, self.drive1Info[0], self.drive1Info[1], self.drive1Info[2], "Root Drive")
        x += w
        # Drive 2
        if self.drive2Info[0] != "None":
            self.icons.drawDrive(x, y, w, h, self.drive2Info[0], self.drive2Info[1], self.drive2Info[2], "2nd Drive")
            x += w
        # Row 2
        x = 0
        y = h
        # CPU Load
        self.icons.drawCPULoad(x, y, w, h, self.cpuLoad[0], self.cpuLoad[1], self.cpuLoad[2])
        x += w
        # Memory
        self.icons.drawMemory(x, y, w, h, self.memoryInfo["label"], self.memoryInfo["percentused"])
        x += w
        # Swap
        self.icons.drawMemory(x, y, w, h, self.swapInfo["label"], self.swapInfo["percentused"])
        x += w
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = SysInfoPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a visual of the system running state with temp, memory, storage used")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()