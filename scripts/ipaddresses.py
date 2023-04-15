#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import psutil
import sys
import vicarioustext

class IPAddressesPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new IP Addresses panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerText", "IP Addresses")
        self._defaultattr("interval", 120)

        # Initialize
        super().__init__(name="ipaddresses")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.netaddresses = psutil.net_if_addrs()

    def run(self):

        super().startImage()

        ipaddresslist = ""
        for netdevicekey in self.netaddresses.keys():
            if netdevicekey == "lo":    # loopback
                continue
            netdevice = self.netaddresses[netdevicekey]
            for netaddress in netdevice:
                family, ipaddress, _, broadcast, _ = netaddress
                if broadcast == None:
                    continue
                if int(family) != 2:    # Restrict to AF_INET (IPv4) address types
                    continue
                ipaddresslist = ipaddresslist + "\n" if len(ipaddresslist) > 0 else ipaddresslist
                ipaddresslist = f"{ipaddresslist}{ipaddress}"

        maxFontSize = int(self.height * 32/320)
        minFontSize = 12
        fs, _, _ = vicarioustext.getmaxfontsize(self.draw, ipaddresslist, self.width, self.getInsetHeight(), True, maxFontSize, minFontSize)
        if fs < minFontSize:
            vicarioustext.drawtoplefttext(self.draw, ipaddresslist, minFontSize, 0, self.getInsetTop(), ImageColor.getrgb(self.textColor), True)
        else:
            vicarioustext.drawcenteredtext(self.draw, ipaddresslist, fs, self.width // 2, self.getInsetTop() + (self.getInsetHeight() // 2), ImageColor.getrgb(self.textColor), True)

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = IPAddressesPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares an image with all the IP addresses used by this host")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()