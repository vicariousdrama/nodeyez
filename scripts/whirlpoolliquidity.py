#! /usr/bin/env python3
from PIL import Image, ImageColor
from datetime import datetime, timedelta
from vicariouspanel import NodeyezPanel
from os.path import exists
import json
import os
import stat
import sys
import time
import vicariousnetwork
import vicarioustext

class WhirlpoolLiquidityPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Whirlpool Liquidity panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorElapsed": "elapsedColor",
            "colorHeader": "headerColor",
            "colorPoolHeader": "poolHeaderColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "apiKey": "apiKey",
            "attributionColor": "attributionColor",
            "confirmedColor": "confirmedColor",
            "elapsedColor": "elapsedColor",
            "poolHeaderColor": "poolHeaderColor",
            "registeredColor": "registeredColor",
            "useTor": "useTor",
            "whirlpoolUrl": "whirlpoolUrl",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("apiKey", "NOT_SET")
        self._defaultattr("attributionColor", "#aa2222")
        self._defaultattr("confirmedColor", "#aaaaaa")
        self._defaultattr("elapsedColor", "#aaaaaa")
        self._defaultattr("headerColor", "#ffffff")
        self._defaultattr("headerText", "Whirlpool Liquidity")
        self._defaultattr("poolHeaderColor", "#aa2222")
        self._defaultattr("premixersColor", "#aaaaaa")
        self._defaultattr("registeredColor", "#aaaaaa")
        self._defaultattr("remixersColor", "#aaaaaa")
        self._defaultattr("interval", 120)
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "bottomright")
        self._defaultattr("whirlpoolUrl", "http://udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion")

        # Initialize
        super().__init__(name="whirlpoolliquidity")

        # Make directories as needed
        d = f"{self.dataDirectory}whirlpool/"
        if not exists(d): os.makedirs(d)
        self.whirlpoolDataDirectory = d

    def fetchData(self):
        """Fetches all the data needed for this panel"""
        self.getLiquidityData()

    def getFileAgeInSeconds(self, pathname):
        if not exists(pathname): return 0
        return time.time() - os.stat(pathname)[stat.ST_MTIME]

    def getLiquidityData(self):
        filepath = self.whirlpoolDataDirectory + "whirlpoolliquidity.json"
        refreshData = False
        if not exists(filepath):
            refreshData = True
        else:
            fileage = self.getFileAgeInSeconds(filepath)
            if fileage > self.interval: refreshData = True
        if refreshData:
            self.log("Refreshing whirlpool liquidity data")
            self.data = vicariousnetwork.getwhirlpoolliquidity(self.useTor, self.whirlpoolUrl, self.apiKey)
            found = False
            remixers, premixers, _, _ = self.getPoolInfo("0.5btc")
            if remixers == -1 or premixers == -1:
                self.log("failed to retrieve valid liquidity data")
                if exists(filepath):
                    self.log("loading stale whirlpool liquidity data")
                    with open(filepath) as f:
                        self.data = json.load(f)
                return
            self.log(f"Saving whirlpool liquidity data to {filepath}")
            with open(filepath, "w") as f:
                json.dump(self.data, f)
        else:
            self.log("Loading cached whirlpool liquidity data")
            with open(filepath) as f:
                self.data = json.load(f)

    def getPoolInfo(self, poolid):
        nbRegistered = -1
        nbConfirmed = -1
        elapsedTime = -1
        setSize = 5
        found = False
        if "pools" in self.data:
            for pool in self.data["pools"]:
                if pool["poolId"] == poolid:
                    found = True
                    if "nbRegistered" in pool: nbRegistered = int(pool["nbRegistered"])
                    if "nbConfirmed" in pool: nbConfirmed = int(pool["nbConfirmed"])
                    if "elapsedTime" in pool: elapsedTime = int(pool["elapsedTime"])
                    if "mixAnonymitySet" in pool: setSize = int(pool["mixAnonymitySet"])
                    break
        if not found:
            self.log(f"did not locate pool with id: {poolid}.")
        return nbRegistered, nbConfirmed, elapsedTime, setSize

    def isWhirlpoolCoordinator(self):
        if "udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion" in self.whirlpoolUrl:
            return True
        if "pool.whirl.mx" in self.whirlpoolUrl:
            return True
        return False

    def getHumanTime(self, timeinms, partcount=1):
        d = timedelta(milliseconds=timeinms)
        seconds = int(d.total_seconds() // 1)
        o = ""
        if partcount > 0 and (seconds // 86400) > 0:
            days = seconds // 86400
            o = o + ", " if len(o) > 0 else o
            o = o + str(days) + " day"
            o = o + "s" if days > 1 else ""
            partcount = partcount - 1
            seconds -= (days * 86400)
        if partcount > 0 and (seconds // 3600) > 0:
            hours = seconds // 3600
            o = o + ", " if len(o) > 0 else o
            o = o + str(hours) + " hour"
            o = o + "s" if hours > 1 else ""
            partcount = partcount - 1
            seconds -= (hours * 3600)
        if partcount > 0 and (seconds // 60) > 0:
            minutes = seconds // 60
            o = o + ", " if len(o) > 0 else o
            o = o + str(minutes) + " minute"
            o = o + "s" if minutes > 1 else ""
            partcount = partcount - 1
        if partcount > 0 and seconds > 0:
            o = o + ", " if len(o) > 0 else o
            o = o + str(seconds) + " second"
            o = o + "s" if seconds > 1 else ""
            partcount = partcount - 1
        if o == "":
            o = "now"
        else:
            o += " ago"
        return o

    def renderPool(self, poolId, label, topx, topy, bottomx, bottomy):
        registered, confirmed, elapsedTime, setSize = self.getPoolInfo(poolId)
        humantime = self.getHumanTime(elapsedTime, 1)
        headersize = int(self.height * 18/320)
        labelsize = int(self.height * 16/320)
        labelbuf = int(self.height * 4/320)
        labelline = 1.1
        whirlsize = 32  # static image width and height, if scale later, adjust
        whirllabelsize = int(self.height * 10/320)
        whirlsetwidth = setSize * whirlsize
        # header
        vicarioustext.drawcenteredtext(self.draw, label, headersize, topx+(bottomx-topx)//2, topy + (headersize // 3 * 2), ImageColor.getrgb(self.poolHeaderColor), True)
        # last cycle
        t = f"Last Cycle: {humantime}"
        vicarioustext.drawcenteredtext(self.draw, t, labelsize, topx+(bottomx-topx)//2, topy + (headersize + (3.2 * labelsize * labelline) + labelbuf), ImageColor.getrgb(self.elapsedColor), False)
        # confirmed whirls
        center = int( topx + (bottomx-topx)//2 + 2 )
        x = center - (whirlsetwidth // 2)
        y = topy + (headersize + (1 * labelsize * labelline) + labelbuf)
        for w in range(setSize):
            c = "green" if confirmed > w else "grey"
            if confirmed > setSize and w + 1 == setSize: c = "grey" # there must be multiple mixes being prepared in one pool
            self.renderWhirl(x + (w * whirlsize), y-(whirlsize//2), c)
        t = f"{confirmed} confirmed"
        y = topy + (headersize + (2.25 * labelsize * labelline) + labelbuf)
        vicarioustext.drawlefttext(self.draw, t, whirllabelsize, x, y, ImageColor.getrgb(self.confirmedColor), False)
        # registered label
        t = f"{registered} registered"
        x = center + (whirlsetwidth // 2)
        y = topy + (headersize + (2.25 * labelsize * labelline) + labelbuf)
        vicarioustext.drawrighttext(self.draw, t, whirllabelsize, x, y, ImageColor.getrgb(self.registeredColor), False)

    def renderAttribution(self):
        attributionLine = "Data from Whirlpool Coordinator" 
        if not self.isWhirlpoolCoordinator(): attributionLine = "Data from Whirlpool Client"
        fontsize = int(self.height * 16/320)
        vicarioustext.drawbottomlefttext(self.draw, attributionLine, fontsize, 0, self.height, ImageColor.getrgb(self.attributionColor))

    def renderSamourai(self, size):
        filepath = "../images/samourai.png"
        if not exists(filepath): return
        im = Image.open(filepath)
        if im.height != size:
            irh = float(im.width)/float(im.height)    
            nw = size
            nh = int(size * irh)
            im2 = im.resize(size=(nw,nh),resample=Image.NEAREST)
            pos = ((self.width//2)-(nw//2), self.getInsetTop()+((self.getInsetHeight()//2)-(nh//2)))
            self.canvas.paste(im2, pos)
            im2.close()
        else:
            pos = ((self.width//2)-(im.width//2),self.getInsetTop()+((self.getInsetHeight()//2)-(im.height//2)))
            self.canvas.paste(im, pos)
        im.close()

    def renderWhirl(self, x, y, c="grey"):
        filepath = f"../images/whirlpool-{c}-32.png"
        if not exists(filepath): return
        im = Image.open(filepath)
        self.canvas.paste(im, (int(x),int(y)))
        im.close()

    def run(self):

        super().startImage()

        # Pools
        qw = self.width // 2
        qh = self.getInsetHeight() // 2
        qx = int(self.height * 35/320)
        self.renderPool("0.5btc","50M Sats", 0, self.getInsetTop(), qw, self.getInsetTop() + qh - qx)
        self.renderPool("0.05btc", "5M Sats", qw+1, self.getInsetTop(), self.width, self.getInsetTop() + qh - qx)
        self.renderPool("0.01btc", "1M Sats", 0, self.getInsetTop() + qh + 1 + qx, qw, self.getInsetBottom())
        self.renderPool("0.001btc", "100K Sats", qw+1, self.getInsetTop() + qh + 1 + qx, self.width, self.getInsetBottom())

        # Samourai Logo
        logosize = int(self.height * 75/320)
        self.renderSamourai(logosize)

        # Attribution
        self.renderAttribution()

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = WhirlpoolLiquidityPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of Whirlpool Liquidity.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()