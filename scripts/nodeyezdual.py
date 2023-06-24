#! /usr/bin/env python3
from PIL import Image, ImageColor
from vicariousicon import VicariousIcons
from vicariouspanel import NodeyezPanel
import numpy
import random
import sys
import vicariousnetwork
import vicariousstat
import vicarioustext

class NodeyezDualPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Dual Display panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "dividerBuffer": "dividerBuffer",
            "dividerHeight": "dividerHeight",
            "headerIconStyle": "headerIconStyle",
            "headerSVG": "headerSVG",
            "topImages": "topImages",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("bottomImages", [
            "https://nodeyez.com/images/fearandgreed.png",
            "https://nodeyez.com/images/fiatprice.png",
            "https://nodeyez.com/images/mempoolblocks.png",
            "https://nodeyez.com/images/satsperfiatunit.png",
            ])
        self._defaultattr("dividerBuffer", 5)
        self._defaultattr("dividerHeight", 10)
        self._defaultattr("footerEnabled", False)
        self._defaultattr("headerEnabled", False)
        self._defaultattr("headerIconStyle", "colorful")
        self._defaultattr("headerSVG", "https://nodeyez.com/images/nodeyez.svg")
        self._defaultattr("height", 800)
        self._defaultattr("interval", 30)
        self._defaultattr("topImages", [
            "https://nodeyez.com/images/arthash.png",
            "https://nodeyez.com/images/blockhashdungeon.png",
            "https://nodeyez.com/images/blockheight.png",
            "https://nodeyez.com/images/lndchannelbalance.png",
            "https://nodeyez.com/images/lndchannelfees.png",
            "https://nodeyez.com/images/difficultyepoch.png",
            "https://nodeyez.com/images/halving.png",
            "https://nodeyez.com/images/utcclock.png",
            ])
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkEnabled", False)
        self._defaultattr("width", 480)

        # Initialize
        super().__init__(name="nodeyezdual")
        self.bottomImage = None
        self.headerImage = None
        self.topImage = None
        self.icons = VicariousIcons()

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        # We only need to retrieve the header image once
        if self.headerImage is None:
            self.headerImage = vicariousnetwork.getimagefromurl(self.useTor, self.headerSVG)

        self.jitterXO = random.randint(0,6)
        self.jitterYO = random.randint(0,3)

        # Setup random accent colors
        accentR = random.randint(48,255)
        accentG = random.randint(48,255)
        accentB = random.randint(48,255)
        self.accentColor3 = (accentR, accentG, accentB)
        self.accentColor4 = (accentR, accentG, accentB, 255)

        # Pick randomly from top and bottom images
        if self.bottomImage is not None: self.bottomImage.close()
        self.bottomImage = self.pickAndScaleImage(self.bottomImages)
        if self.topImage is not None: self.topImage.close()
        self.topImage = self.pickAndScaleImage(self.topImages)

        # System Info
        self.cpuLoad = vicariousstat.getload()
        self.cpuTemp = vicariousstat.getcputemp()
        self.drive1Info = vicariousstat.getdrive1info()
        self.drive2Info = vicariousstat.getdrive2info()
        self.memoryAvailable = vicariousstat.getmemoryavailable()
        self.networkReceived = vicariousstat.getnetworkrx()
        self.networkTransmitted = vicariousstat.getnetworktx()
        self.uptime = vicariousstat.getuptime()

    def pickAndScaleImage(self, list):
        found = False
        count = 10
        while (not found) and (count > 0):
            url = random.choice(list)
            im = vicariousnetwork.getimagefromurl(False, url)
            found = im.width > 1
            count = count - 1
        if not found: im = im.convert('RGBA')
        return self.resizeImageToWidth(im)

    def recolor(self, imInput, fromRGB, toRGB):
        im = imInput.convert('RGBA')
        data = numpy.array(im)
        red,green,blue,alpha = data.T
        colorset = (red==fromRGB[0]) & (green==fromRGB[1]) & (blue==fromRGB[2])
        data[...,:-1][colorset.T]=toRGB
        imOutput = Image.fromarray(data)
        return imOutput

    def run(self):

        super().startImage()

        # Header logo
        headerImageColor = self.recolor(self.headerImage, (102,102,102), self.accentColor3)
        headerImageColor = self.resizeImageToWidth(headerImageColor)
        self.canvas.alpha_composite(im=headerImageColor,dest=(self.jitterXO,self.jitterYO))

        # System Info Icons
        self.icons.draw = self.draw
        self.icons.drivePieEmptyTextColor = self.accentColor4
        self.icons.setLabelTextColor(self.accentColor4)
        self.icons.setOutlineColor(self.accentColor4)
        if self.headerIconStyle == "monochromatic":
            self.icons.setDangerFillColor(self.accentColor4)
            self.icons.setGoodFillColor(self.accentColor4)
            self.icons.setWarnFillColor(self.accentColor4)
        w = self.width // 6
        h = w
        x = self.jitterXO
        y = self.jitterYO + headerImageColor.height + 2
        labelsize=int(h*.15)
        self.icons.drawThermometer(x, y, w, h, self.cpuTemp)
        x += w
        self.icons.drawDrive(x, y, w, h, self.drive1Info[0], self.drive1Info[1], self.drive1Info[2], "Root Drive")
        x += w
        if self.drive2Info[0] != "None":
            self.icons.drawDrive(x, y, w, h, self.drive2Info[0], self.drive2Info[1], self.drive2Info[2], "2nd Drive")
            x += w
        self.icons.drawCPULoad(x, y, w, h, self.cpuLoad[0], self.cpuLoad[1], self.cpuLoad[2])
        x += w
        # System Info Text
        x += 10
        vicarioustext.drawlefttext(self.draw, "Avail. Mem:    ", labelsize, x, y+(h*.08), self.accentColor4, True)
        vicarioustext.drawlefttext(self.draw, "Net Data Rx:   ", labelsize, x, y+(h*.33), self.accentColor4, True)
        vicarioustext.drawlefttext(self.draw, "Net Data Tx:   ", labelsize, x, y+(h*.58), self.accentColor4, True)
        vicarioustext.drawlefttext(self.draw, "Uptime:        ", labelsize, x, y+(h*.83), self.accentColor4, True)
        td = vicarioustext.gettextdimensions(self.draw, "Net Data Rx:   ", labelsize)
        x += td[0]
        vicarioustext.drawlefttext(self.draw, str(self.memoryAvailable) + "M", labelsize, x, y+(h*.08), self.accentColor4)
        vicarioustext.drawlefttext(self.draw, self.networkReceived, labelsize, x, y+(h*.33), self.accentColor4)
        vicarioustext.drawlefttext(self.draw, self.networkTransmitted, labelsize, x, y+(h*.58), self.accentColor4)
        vicarioustext.drawlefttext(self.draw, self.uptime, labelsize, x, y+(h*.83), self.accentColor4)
        td = vicarioustext.gettextdimensions(self.draw, self.uptime, labelsize)
        x += td[0]
        topy = y + h

        # Images
        y = self.height
        # Bottom Image
        y -= self.bottomImage.height
        if y >= topy: self.canvas.paste(self.bottomImage, box=(0,y))
        # Divider
        y -= self.dividerBuffer if self.dividerBuffer > 0 else 0
        if self.dividerHeight > 0:
            y -= self.dividerHeight
            if y >= topy: self.draw.rectangle(xy=((0,y),(self.width,y+self.dividerHeight)),fill=self.accentColor4)
        y -= self.dividerBuffer if self.dividerBuffer > 0 else 0
        # Top Image
        y -= self.topImage.height
        if y >= topy: self.canvas.paste(self.topImage, box=(0,y))

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = NodeyezDualPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves existing images and builds a composite of two stacked on top of each other for Nodeyez in portrait orientation")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()