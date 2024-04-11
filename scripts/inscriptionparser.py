#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw, ImageFile
from io import BytesIO
from vicariouspanel import NodeyezPanel
import exifread
import logging
import os
import re
import sys
import time
import vicariousbitcoin
import vicariouslookup
import vicarioustext
import wand.color
import wand.image

class InscriptionParser(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Inscription Parser panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "exportFilesToDataDirectory": "exportFilesEnabled",
            "overlayTextColorBG": "overlayBackgroundColor",
            "overlayTextFG": "overlayTextColor",
            "sleepInterval": "interval",
            # panel specific key names
            "exportFilesEnabled": "exportFilesEnabled",
            "overlayBackgroundColor": "overlayBackgroundColor",
            "overlayEnabled": "overlayEnabled",
            "overlayExifEnabled": "overlayExifEnabled",
            "overlayTextColor": "overlayTextColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("exportFilesEnabled", True)
        self._defaultattr("footerEnabled", False)
        self._defaultattr("interval", 60)
        self._defaultattr("overlayBackgroundColor", "#00000040")
        self._defaultattr("overlayEnabled", True)
        self._defaultattr("overlayExifEnabled", True)
        self._defaultattr("overlayTextColor", "#ffffffff")
        self._defaultattr("watermarkAnchor", "topleft")

        # Initialize
        super().__init__(name="inscriptionparser")
        self.previousblock = 0

        # Create additional folders expected for this panel
        self.inscriptionsDir = f"{self.dataDirectory}inscriptions/"
        if not os.path.exists(self.inscriptionsDir):
            os.makedirs(self.inscriptionsDir)

        # Support truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES=True


    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blocknumber = vicariousbitcoin.getcurrentblock()
        if self.previousblock == self.blocknumber: return
        if self.previousblock > 0: self.blocknumber = self.previousblock + 1
        self.log(f"Fetching inscriptions for {self.blocknumber}")
        t1 = int(time.time())
        self.inscriptions = vicariousbitcoin.getblockinscriptions(self.blocknumber)
        t2 = int(time.time())
        self.log(f"{t2 - t1} seconds")

    def exportInscription(self, inscription):
        fileExtension = self.getFileExtension(inscription)
        txid = inscription["txid"]
        txidx = inscription["txidx"]
        exportFileName = f"{self.blockDir}inscription-{self.blocknumber}-{txidx:05}-{txid}.{fileExtension}"
        bytesioblob = BytesIO(inscription["data"])
        with open(exportFileName, "wb") as f:
            f.write(bytesioblob.getbuffer())

    def getMimeType(self, inscription):
        contenttype = inscription["contenttype"] if "contenttype" in inscription else "undefined"
        mimetype = contenttype.split(";")[0]
        return mimetype

    def getExifTags(self, inscription):
        exif = {}
        if not self.overlayExifEnabled: return exif
        mimetype = self.getMimeType(inscription)
        if mimetype not in ["image/gif","image/jpeg","image/png","image/webp"]: return exif
        exifread.logger.setLevel(logging.ERROR) # Dont report if file does not have exif data
        tags = exifread.process_file(BytesIO(inscription["data"]), details=False)
        for tag in tags.keys():
            if tag in ["Image Orientation","EXIF UserComment","Image Make","Image Model","EXIF LensModel"]:
                exif[tag] = tags[tag]
            elif tag in ["ImageWidth","EXIF ExifImageWidth"]:
                exif["ImageWidth"] = tags[tag]
            elif tag in ["ImageLength","EXIF ExifImageLength"]:
                exif["ImageLength"] = tags[tag]
            elif tag in ["DateTime", "Image DateTime", "EXIF DateTimeOriginal", "EXIF DateTimeDigitized"]:
                exif["DateTime"] = tags[tag]
            elif tag in ["Software","Image Software"]:
                exif["Software"] = tags[tag]
        return exif

    def getFileExtension(self, inscription):
        r = "bin"
        mt = self.getMimeType(inscription)
        if mt in vicariouslookup.MimeTypeToFileExtension:
            r = vicariouslookup.MimeTypeToFileExtension[mt]
        return r

    def renderOverlayInfo(self, inscription):
        exif = self.getExifTags(inscription)
        mimetype = self.getMimeType(inscription)
        mimetypestr = f"mimetype: {mimetype}"
        size = int(inscription["size"]) if "size" in inscription else 0
        txsize = inscription["txsize"]
        parentsize = inscription["parentsize"]
        totalsize = txsize + parentsize
        sizestr = f"data size: {size}, tx size: {txsize}, commitment tx size: {parentsize}, total size: {totalsize}"
        txid = inscription["txid"]
        txidstr = f"txid: {txid}"
        fontsize = int(self.height * 11/320) # so txid will fit

        overlayimg = Image.new(mode="RGBA", size=(self.width,self.height), color=(0,0,0,0))
        overlaydraw = ImageDraw.Draw(overlayimg)

        # calculate overall sizes
        txidstrw, txidstrh, _ = vicarioustext.gettextdimensions(overlaydraw, txidstr, fontsize)
        sizestrw, sizestrh, _ = vicarioustext.gettextdimensions(overlaydraw, sizestr, fontsize)
        mimetypestrw, mimetypestrh, _ = vicarioustext.gettextdimensions(overlaydraw, mimetypestr, fontsize)
        maxw = max(txidstrw,sizestrw)
        maxw = max(maxw,mimetypestrw)
        exifheight = 0
        for k in exif: 
            v = exif[k]
            s = f"{k}: {v}"
            ew, eh, _ = vicarioustext.gettextdimensions(overlaydraw, s, fontsize)
            exifheight += eh
            maxw = max(maxw,ew)

        # background
        y = self.getInsetTop() + self.getInsetHeight()
        y2 = y - txidstrh - sizestrh - mimetypestrh - exifheight
        overlaydraw.rectangle(xy=((self.width-maxw,y),(self.width,y2)),fill=ImageColor.getrgb(self.overlayBackgroundColor))

        # annotations
        # txid
        vicarioustext.drawbottomrighttext(overlaydraw, txidstr, fontsize, self.width, y, ImageColor.getrgb(self.overlayTextColor))
        y -= txidstrh
        # size
        vicarioustext.drawbottomrighttext(overlaydraw, sizestr, fontsize, self.width, y, ImageColor.getrgb(self.overlayTextColor))
        y -= sizestrh
        # mimetype
        vicarioustext.drawbottomrighttext(overlaydraw, mimetypestr, fontsize, self.width, y, ImageColor.getrgb(self.overlayTextColor))
        y -= mimetypestrh
        # exif
        for k in exif: 
            v = exif[k]
            s = f"{k}: {v}"
            _, eh, _ = vicarioustext.gettextdimensions(overlaydraw, s, fontsize)
            vicarioustext.drawbottomrighttext(overlaydraw, s, fontsize, self.width, y, ImageColor.getrgb(self.overlayTextColor))
            y -= eh

        self.canvas.alpha_composite(overlayimg)
        overlayimg.close()

    def run(self):

        if self.previousblock == self.blocknumber:
            self._markAsRan()
            return
        self.previousblock = self.blocknumber

        if len(self.inscriptions) == 0:
            self.log(f"No inscriptions found in block {self.blocknumber}")
            self._markAsRan()
            return
        else:
            self.log(f"Processing {len(self.inscriptions)} inscriptions in block {self.blocknumber}")

        self.headerText = f"Inscription in {self.blocknumber}"
        blockDir = f"{self.inscriptionsDir}"
        blockstr = str(self.blocknumber)
        while len(blockstr) > 0:
            bnpart = blockstr[:1]
            blockstr = blockstr[1:]
            blockDir = f"{blockDir}{bnpart}/"
        self.blockDir = blockDir
        if self.exportFilesEnabled and not os.path.exists(self.blockDir): 
            os.makedirs(self.blockDir)

        # track if we found an image to use for the panel
        foundImage = False

        typecount = {}

        for inscription in self.inscriptions:
            # extract files
            if self.exportFilesEnabled: self.exportInscription(inscription)
            mimetype = self.getMimeType(inscription)
            # track statistics by mime type
            typecount[mimetype] = 1 if mimetype not in typecount else typecount[mimetype] + 1
            # only proceed if not yet processed an image
            if foundImage: continue
            if mimetype not in ["image/gif","image/jpeg","image/png","image/svg","image/svg+xml","image/webp"]: continue
            if mimetype not in ["image/gif","image/jpeg","image/png"]: continue
            # retrieving image depends on file format for handler
            if mimetype in ["image/gif","image/jpeg","image/png","image/webp"]:
                img = Image.open(BytesIO(inscription["data"])).convert('RGBA')
            elif mimetype in ["image/svg", "image/svg+xml"]:
                with wand.image.Image() as image:
                    image.read(blob=BytesIO(inscription["data"]),format="svg")
                    img = Image.open(BytesIO(image.make_blob("png32")))
            else:
                img=Image.new(mode="RGB",size=(1,1),color=ImageColor.getrgb("#7f007f")) # default if not loaded from type
            # build the image for the panel
            super().startImage()
            # Resize to fit
            img = self.resizeImageToInset(img)
            # Paste it
            xpos = (self.canvas.width - img.width)//2
            self.canvas.paste(img, box=(xpos,self.getInsetTop()))
            img.close()
            # Overlay
            if self.overlayEnabled: self.renderOverlayInfo(inscription)
            super().finishImage()
            foundImage = True

        # report statistics
        self.log("Inscription count by mime type")
        for k,v in sorted(typecount.items()): self.log(f"- {k}: {v}")

        self._markAsRan()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = InscriptionParser()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
        if arg1 in ['-h','--help']:
            arg0 = sys.argv[0]
            print(f"Produces an image with an Inscription. May be configured to parse all inscriptions")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
            print(f"   If a number is provided, it will be treated as a block number to look for inscriptions")
            print(f"   {arg0} 722231")
        else:
            p.blocknumber = vicariousbitcoin.getcurrentblock()
            if re.match(r'^-?\d+$', arg1) is not None:
                if int(arg1) <= p.blocknumber: 
                    p.blocknumber = int(arg1)
            p.inscriptions = vicariousbitcoin.getblockinscriptions(p.blocknumber)
            # p.opreturns = vicariousbitcoin.getblockopreturns(p.blocknumber)
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()
