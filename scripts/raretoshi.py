#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw, ImageFile
from os.path import exists
from vicariouspanel import NodeyezPanel
import json
import os
import qrcode
import random
import re
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

class RaretoshiPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Raretoshi panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "qrCodeSize": "qrCodePizelSize",
            "overlayTextEnabled": "overlayEnabled",
            "overlayTextColorBG": "overlayBackgroundColor",
            "overlayTextColorFG": "overlayTextColor",
            "sleepInterval": "interval",
            # panel specific key names
            "overlayBackgroundColor": "overlayBackgroundColor",
            "overlayEnabled": "overlayEnabled",
            "overlayTextColor": "overlayTextColor",
            "qrCodeEnabled": "qrCodeEnabled",
            "qrCodePixelSize": "qrCodePixelSize",
            "randomUserEnabled": "randomUserEnabled",
            "randomUserInterval": "randomUserInterval",
            "stretchEdgeEnabled": "stretchEdgeEnabled",
            "stretchEdgeSpacing": "stretchEdgeSpacing",
            "raretoshiUser": "raretoshiUser",
            "useTor": "useTor",
            "userInfoInterval": "userInfoInterval",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("footerEnabled", False)
        self._defaultattr("headerText", "Raretoshi Image")
        self._defaultattr("interval", 120)
        self._defaultattr("overlayBackgroundColor", "#00000080")
        self._defaultattr("overlayEnabled", True)
        self._defaultattr("overlayTextColor", "#ffffff")
        self._defaultattr("qrCodeEnabled", True)
        self._defaultattr("qrCodePixelSize", 2)
        self._defaultattr("randomUserEnabled", True)
        self._defaultattr("randomUserInterval", 300)
        self._defaultattr("raretoshiUser", "valeriyageorg")
        self._defaultattr("stretchEdgeEnabled", True)
        self._defaultattr("stretchEdgeSpacing", 30)
        self._defaultattr("useTor", True)
        self._defaultattr("userInfoInterval", 3600)
        self._defaultattr("watermarkEnabled", False)

        # Initialize
        super().__init__(name="raretoshi")

        # Make directories as needed
        d = f"{self.dataDirectory}ipfs/"
        if not exists(d): os.makedirs(d)
        self.ipfsDataDirectory = d
        d = f"{self.dataDirectory}raretoshi/"
        if not exists(d): os.makedirs(d)
        self.raretoshiDataDirectory = d

        # Set starting state
        self.collectionIndex=-1
        self.userInfoLast=0
        self.userInfo={"subject":{"holdings":[]}}
        self.randomUserLast=0
        self.loadUsernames()

        # Support truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES=True

    def getValuesForKeyname(self, o, keyName="username"):
        values = []
        for key, value in o.items():
            if key == keyName:
                if type(value) is str and value not in values: values.append(value)
            else:
                if type(value) is list:
                    for listItem in value:
                        if type(listItem) is str and listItem not in values: values.append(listItem)
                        if type(listItem) is dict:
                            dictValues = self.getValuesForKeyname(listItem, keyName)
                            for dictValue in dictValues:
                                if dictValue not in values: values.append(dictValue)
                if type(value) is dict:
                    dictValues = self.getValuesForKeyname(value, keyName)
                    for dictValue in dictValues:
                        if dictValue not in values: values.append(dictValue)
        return values

    def loadUsernames(self):
        self.usernames=vicariousbitcoin.loadJSONData(f"{self.raretoshiDataDirectory}/raretoshi-usernames.json", [self.raretoshiUser])

    def saveUsernames(self):
        with open(f"{self.raretoshiDataDirectory}/raretoshi-usernames.json", "w") as f:
            json.dump(self.usernames, f)

    def setupRaretoshiUser(self):
        now = int(time.time())
        if self.randomUserInterval + self.randomUserLast > now: return
        self.randomUserLast = now
        usernames = self.getValuesForKeyname(self.userInfo, "username")
        self.usernames = list(set(self.usernames + usernames))
        if len(self.usernames) > 0: self.raretoshiUser = random.choice(self.usernames)
        self.saveUsernames()

    def setupHoldingInfo(self):
        self.holding = None
        allowedFileTypes = ['image/png','image/jpeg']
        holdingsCount = len(self.userInfo["subject"]["holdings"])
        holdingIndex = self.collectionIndex
        fileType = ""
        # quick bail if no holdings
        if holdingsCount == 0:
            self.log(f"User {self.raretoshiUser} has no holdings on raretoshi")
            return
        # check if requested index exists and suitable
        if holdingIndex > -1 and holdingIndex < holdingsCount:
            holding = self.userInfo["subject"]["holdings"][holdingIndex]
            if self.isValidHoldingFormat(holding):
                fileType = holding["filetype"]
                if fileType not in allowedFileTypes:
                    self.log(f"Holding #{holdingIndex} is '{fileType}' which is unsupported.")
            else:
                self.log(f"Holding #{holdingIndex} is not valid format.")
        # Pick randomly if not yet suitable
        holdingChecked = [holdingIndex]
        holdingChecks = 8
        while (fileType not in allowedFileTypes) and (holdingChecks > 0):
            holdingChecks -= 1
            while holdingIndex in holdingChecked and len(holdingChecked) < holdingsCount:
                holdingIndex = int(random.random() * holdingsCount)
            holdingChecked.append(holdingIndex)
            holding = self.userInfo["subject"]["holdings"][holdingIndex]
            if self.isValidHoldingFormat(holding):
                fileType = holding["filetype"] if "filetype" in holding else ""
                if fileType not in allowedFileTypes:
                    self.log(f"Holding #{holdingIndex} is '{fileType}' which is unsupported.")
            else:
                self.log(f"Holding #{holdingIndex} is not valid format.")
        if fileType not in allowedFileTypes:
            self.log(f"User {self.raretoshiUser} has no suitable holdings on raretoshi matching allowed types {allowedFileTypes}")
            return
        if self.isValidHoldingFormat(holding): self.holding = holding

    def downloadIPFSfile(self, ipfshash):
        downloadFromRaretoshi = False
        if ipfshash.endswith(".png") or ipfshash.endswith(".jpeg"):
            # seems that avatar_url for artist and owner may not be in ipfs.io.
            # these urls also contain the file extension, which needs to be removed
            downloadFromRaretoshi = True
            ipfshash = ipfshash.replace(".png", "")
            ipfshash = ipfshash.replace(".jpeg", "")
        saveto = self.ipfsDataDirectory + ipfshash
        if exists(saveto):
            self.log(f"Skipping IPFS download. File already exists at {saveto}")
            return 0
        if downloadFromRaretoshi:
            url = "https://raretoshi.com/api/ipfs/" + ipfshash
        else:
            url = "https://ipfs.io/ipfs/" + ipfshash
        self.log(f"Downloading from {url}")
        rc = vicariousnetwork.getandsavefile(self.useTor, url, saveto, "")
        if rc == 0:
            self.log(f"IPFS Downloaded to {saveto}")
        else:
            # If we were originally hitting IPFS, we can try fallback to raretoshi
            if url.startswith("https://ipfs.io/"):
                url = url.replace("https://ipfs.io/", "https://raretoshi.com/api/")
                self.log(f"Retrying with {url}")
                rc = vicariousnetwork.getandsavefile(self.useTor, url, saveto, "")
                if rc == 0:
                    self.log(f"IPFS Downloaded to {saveto}")
                else:
                    self.log(f"Unable to download file from {url}")
        return rc

    def isValidUserFormat(self, user):
        return user.keys() & {'username', 'avatar_url'}

    def isValidHoldingFormat(self, holding):
        if not holding.keys() & {'artist','edition','editions','filename','filetype','owner','slug','title'}: return False
        if not self.isValidUserFormat(holding["artist"]): return False
        if not self.isValidUserFormat(holding["owner"]): return False
        return True

    def downloadFiles(self):
        ipfshash = self.holding["filename"]
        rc1 = self.downloadIPFSfile(ipfshash)
        artist = self.holding["artist"]["username"]
        print(f"Downloading avatar for artist: {artist}")
        rc2 = self.downloadIPFSfile(self.holding["artist"]["avatar_url"])
        owner = self.holding["owner"]["username"]
        print(f"Downloading avatar for owner: {owner}")
        rc3 = self.downloadIPFSfile(self.holding["owner"]["avatar_url"])
        return rc1 # + rc2 + rc3

    def loadAndPasteImage(self):
        ipfshash = self.holding["filename"]
        sourceFile = self.ipfsDataDirectory + ipfshash
        sourceImage=Image.open(sourceFile)
        sourceImage=sourceImage.convert("RGBA")
        sourceImage = self.resizeImageToInset(sourceImage)
        sourceWidth=int(sourceImage.getbbox()[2])
        sourceHeight=int(sourceImage.getbbox()[3])
        sourceLeft = (self.getInsetWidth() - sourceWidth) // 2
        sourceTop = self.getInsetTop() + ((self.getInsetHeight() - sourceHeight) // 2)
        self.canvas.paste(sourceImage, (sourceLeft,sourceTop))
        if self.stretchEdgeEnabled:
            # left
            if sourceLeft - self.stretchEdgeSpacing > 0:
                imLine = sourceImage.crop((0,0,1,sourceHeight))
                for x in range(0,sourceLeft-self.stretchEdgeSpacing):
                    self.canvas.paste(imLine, (x, sourceTop))
            # right
            if sourceLeft + sourceWidth + self.stretchEdgeSpacing < self.width:
                imLine = sourceImage.crop((sourceWidth-1,0,sourceWidth,sourceHeight))
                for x in range(sourceLeft+sourceWidth+self.stretchEdgeSpacing,self.getInsetWidth()):
                    self.canvas.paste(imLine, (x, sourceTop))
            # top
            if sourceTop - self.stretchEdgeSpacing > self.getInsetTop():
                imLine = sourceImage.crop((0,0,sourceWidth,1))
                for y in range(self.getInsetTop(),sourceTop-self.stretchEdgeSpacing):
                    self.canvas.paste(imLine, (sourceLeft, y))
            # bottom
            if sourceTop + sourceHeight + self.stretchEdgeSpacing < self.getInsetTop() + self.getInsetHeight():
                imLine = sourceImage.crop((0,sourceHeight-1,sourceWidth,sourceHeight))
                for y in range(sourceTop+sourceHeight+self.stretchEdgeSpacing, self.getInsetTop() + self.getInsetHeight()):
                    self.canvas.paste(imLine, (sourceLeft, y))
        sourceImage.close()

    def renderAnnotation(self):
        if not self.overlayEnabled: return
        overlay = Image.new(mode="RGBA", size=(self.width, self.height), color=(255,255,255,0))
        overlaydraw = ImageDraw.Draw(overlay)
        fontsize = int(self.height * 12 / 320)
        overlayBG = ImageColor.getrgb(self.overlayBackgroundColor)
        overlayFG = ImageColor.getrgb(self.overlayTextColor)
        artist = self.holding["artist"]["username"]
        owner = self.holding["owner"]["username"]
        edition = self.holding["edition"]
        editions = self.holding["editions"]
        editionText = f"Edition: {edition}/{editions}"
        if int(editions) == 1: editionText = f"Edition: One of a Kind"
        listprice = self.holding["list_price"] if "list_price" in self.holding else None
        x = 0
        y = self.getInsetTop() + self.getInsetHeight()
        t = "Asset from Raretoshi.com"
        if self.qrCodeEnabled: t = f"{t} - scan QR code ->"
        fontsize2 = int(self.height * 16 / 320)
        w,h,_ = vicarioustext.gettextdimensions(overlaydraw, t, fontsize2, False)
        h = (fontsize2 * 1.4) // 1
        overlaydraw.rectangle(xy=((x,y),(w,y-h)),fill=overlayBG)
        vicarioustext.drawbottomlefttext(overlaydraw, t, fontsize2, x, y, overlayFG, False)
        y -= h
        if listprice is not None and int(listprice) > 0:
            t = f"List Price: {listprice}"
            w,h,_ = vicarioustext.gettextdimensions(overlaydraw, t, fontsize, False)
            h = (fontsize * 1.4) // 1
            overlaydraw.rectangle(xy=((x,y),(w,y-h)),fill=overlayBG)
            vicarioustext.drawbottomlefttext(overlaydraw, t, fontsize, x, y, overlayFG, False)
            y -= h
        t = editionText
        w,h,_ = vicarioustext.gettextdimensions(overlaydraw, t, fontsize, False)
        h = (fontsize * 1.4) // 1
        overlaydraw.rectangle(xy=((x,y),(w,y-h)),fill=overlayBG)
        vicarioustext.drawbottomlefttext(overlaydraw, t, fontsize, x, y, overlayFG, False)
        y -= h
        t = f"Owner: {owner}"
        w,h,_ = vicarioustext.gettextdimensions(overlaydraw, t, fontsize, False)
        h = (fontsize * 1.4) // 1
        overlaydraw.rectangle(xy=((x,y),(w,y-h)),fill=overlayBG)
        vicarioustext.drawbottomlefttext(overlaydraw, t, fontsize, x, y, overlayFG, False)
        y -= h
        t = f"Artist: {artist}"
        w,h,_ = vicarioustext.gettextdimensions(overlaydraw, t, fontsize, False)
        h = (fontsize * 1.4) // 1
        overlaydraw.rectangle(xy=((x,y),(w,y-h)),fill=overlayBG)
        vicarioustext.drawbottomlefttext(overlaydraw, t, fontsize, x, y, overlayFG, False)
        y -= h
        self.canvas.alpha_composite(overlay)
        overlay.close()

    def renderQRCode(self):
        if not self.qrCodeEnabled: return
        slug=self.holding["slug"]
        raretoshiurl=f"https://raretoshi.com/a/{slug}"
        qr = qrcode.QRCode(box_size=self.qrCodePixelSize)
        qr.add_data(raretoshiurl)
        qr.make()
        img = qr.make_image()
        s = img.size[1]
        pos = (self.getInsetWidth()-s,self.getInsetTop()+self.getInsetHeight()-s)
        self.canvas.paste(img, pos)
        img.close()

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        userInfo, userInfoLast = vicariousnetwork.getraretoshiuserinfo(
            self.useTor, 
            self.raretoshiDataDirectory, 
            self.raretoshiUser, 
            self.userInfo, 
            self.userInfoLast, 
            self.userInfoInterval)
        self.userInfo = userInfo
        self.userInfoLast = userInfoLast

        self.setupHoldingInfo()

        if self.holding is not None: 
            rc = self.downloadFiles()
            if rc > 0: self.holding = None

        if self.randomUserEnabled: self.setupRaretoshiUser()

    def run(self):

        if self.holding is None:
            self.log("Holding not available. Skipping image creation")
            self._markAsRan()
            return

        super().startImage()
        self.headerText = self.holding["title"]
        self.loadAndPasteImage()
        self.renderAnnotation()
        self.renderQRCode()
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = RaretoshiPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
        if arg1 in ['-h','--help']:
            arg0 = sys.argv[0]
            print(f"Prepares an image from the raretoshi colletion for a user, scales and annotates")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired raretoshi user (case sensitive) as an argument as follows")
            print(f"   {arg0} valeriyageorg")
            print(f"3) Pass the desired raretoshi user and an index number")
            print(f"   {arg0} valeriyageorg 3")
        else:
            if len(sys.argv) > 2:
                arg2 = sys.argv[2]
                if re.match(r'^-?\d+$', arg2) is not None:
                    if int(arg2) >= 0: p.collectionIndex = arg2
            p.raretoshiUser = arg1
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()