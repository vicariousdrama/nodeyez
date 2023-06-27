#! /usr/bin/env python3
from PIL import Image, ImageFile
from io import BytesIO
from mimetypes import guess_extension, guess_type
from vicariouspanel import NodeyezPanel
import glob
import json
import os
import re
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

class InscriptionMempoolPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Inscription Mempool panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
        }

        # Directives
        ImageFile.LOAD_TRUNCATED_IMAGES=True

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("extensionsToExtract", ["bmp","gif","jpg","png","svg"])
        self._defaultattr("headerEnabled", True)
        self._defaultattr("headerText", "Recent Unmined Image Inscriptions In Mempool")
        self._defaultattr("interval", 60)

        # Initialize
        super().__init__(name="inscriptionmempool")

        # Create additional folders expected for this panel
        inscriptionMempoolDir = f"{self.dataDirectory}inscription-mempool/"
        if not os.path.exists(inscriptionMempoolDir):
            os.makedirs(inscriptionMempoolDir)

        # Load any previous known data between runs
        self.inscriptionMempoolDir = inscriptionMempoolDir
        self.notInscriptions = vicariousbitcoin.loadJSONData(f"{inscriptionMempoolDir}/data-notinscriptions.json", [])
        self.inscriptions = vicariousbitcoin.loadJSONData(f"{inscriptionMempoolDir}/data-inscriptions.json", [])

        # Build content types for extensions to extract
        self.contentTypesToExtract = self._getContentTypesFromExtensions()

    def _getContentTypesFromExtensions(self):
        contentTypes = []
        for e in self.extensionsToExtract:
            if e == "svg":
                contentTypes.append("image/svg")
                contentTypes.append("image/svg+xml")
            elif e == "webp":
                contentTypes.append("image/webp")
            else:
                atype, _ = guess_type(f"somefile.{e}")
                if atype is not None:
                    contentTypes.append(atype)
        return contentTypes

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        # get mempool
        self.log(f"checking mempool at {vicarioustext.getdateandtime()}")
        self.mempool = vicariousbitcoin.getmempool()

    def _getFileExtensionFromContentType(self, ct):
        r = "bin"        
        mt = ct.split(";")[0]
        femap = {
            "application/x-javascript": "js",
            "application/x-msaccess": "mdb",
            "audio/midi": "midi",
            "image/svg": "svg",
            "image/webp": "webp",
            "image/x-icon": "ico",
            "text/htm": "htm",
            "video/quicktime": "qt",
            "x-word/x-vrml": "vrml",
        }
        if mt in femap:
            r = femap[mt]
        else:
            r = guess_extension(mt)
            r = "bin" if r is None else r.rpartition(".")[2]
        return r

    def _getBaseFilenameForTXID(self, txid):
        return f"{self.inscriptionMempoolDir}inscription-{txid}"

    def _getInscriptionsForTX(self, txid):
        inscriptions = []
        tx = vicariousbitcoin.gettransaction(txid)
        thepattern = re.compile("(.*)0063036f72640101(.*)68$")  # OP_FALSE OP_IF push-3-bytes 'ord' push-1-byte 1
        txidx = -1
        if "vin" not in tx: return inscriptions
        for vin in tx["vin"]:
            if "txinwitness" not in vin: continue
            for txinwitness in vin["txinwitness"]:
                regexmatch = re.match(thepattern, txinwitness)
                if regexmatch is None: continue
                # This is an ordinal inscription.
                txidx += 1
                g2 = regexmatch.group(2)
                pos = 0
                contenttypelength = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                pos += 2
                contenttype = bytes.fromhex(g2[pos:pos+(contenttypelength*2)]).decode()
                # only proceed for those content types matching types we want to extract
                if contenttype not in self.contentTypesToExtract: continue
                pos += (contenttypelength*2)
                opcode = g2[pos:pos+2]
                pos += 2
                if opcode != '00':
                    self.log(f"warning. expected 0x00 divider between content type and data, but got 0x{opcode}")
                datalengthtype = g2[pos:pos+2]
                pos +=2
                datalen = 0
                totaldatalen = 0
                rawbytes = bytearray()
                while datalengthtype in ['4c','4d','4e']:
                    #self.log(f"- hex code for data length: {datalengthtype}")
                    if datalengthtype == "4c": # next 1 byte = size of data
                        datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                        pos += 2
                    if datalengthtype == "4d": # next 2 bytes = size of data
                        datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+4]),"little")
                        pos += 4
                    if datalengthtype == "43": # next 4 bytes = size of data
                        datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+8]),"little")
                        pos += 8
                    totaldatalen += datalen
                    morebytes = bytes.fromhex(g2[pos:pos+(datalen*2)])
                    rawbytes.extend(morebytes)
                    pos += (datalen*2)
                    # see if more op codes to continue data
                    datalengthtype = g2[pos:pos+2]
                    pos += 2
                # Check for extra bytes trailing into end. For now, we'll append these to existing, but this may be incorrect
                remaininghex = g2[pos:]
                remaininghexlength = len(remaininghex)
                if remaininghexlength > 0:
                    morebytes = bytes.fromhex(g2[pos:])
                    rawbytes.extend(morebytes)
                    totaldatalen += (remaininghexlength/2)
                # append an object
                inscription = {"txid":txid,"txidx":txidx,"contenttype":contenttype,"data":rawbytes}
                inscriptions.append(inscription)
        return inscriptions

    def _extractTX(self, txid="00"):
        inscriptions = self._getInscriptionsForTX(txid)
        inscriptionCount = len(inscriptions)
        if inscriptionCount == 0:
            self.notInscriptions.append(txid)
            return inscriptionCount

        for inscription in inscriptions:
            txidx = int(inscription["txidx"]) if "txidx" in inscription else -1
            contentType = inscription["contenttype"] if "contenttype" in inscription else "undefined"
            fileExtension = self._getFileExtensionFromContentType(contentType)
            if fileExtension not in self.extensionsToExtract: continue
            baseFileName = self._getBaseFilenameForTXID(txid)
            exportFileName = f"{baseFileName}-{txidx}.{fileExtension}"
            # self.log(f"exporting file to {exportFileName}")
            try:
                bytesioblob = BytesIO(inscription["data"])
                with open(exportFileName, "wb") as f:
                    f.write(bytesioblob.getbuffer())
            except Exception as e:
                self.log(f"error processing inscription: {e}")
                self.log(f"txid: {txid}, txidx: {txidx}, content-type: {contentType}")

        self.inscriptions.append(txid)
        return inscriptionCount

    def _getMostRecentImagesOfType(self, extension):
        globpath = f"{self.inscriptionMempoolDir}inscription-*.{extension}"
        return list(filter(os.path.isfile, glob.glob(globpath)))

    def _getMostRecentImages(self, max):
        filelist = []
        for e in self.extensionsToExtract:
            filelist.extend(self._getMostRecentImagesOfType(e))    
        filelist.sort(key=os.path.getctime)
        limitedlist = filelist[max*-1:]
        reversedlist = limitedlist[::-1]
        return reversedlist

    def run(self):

        # reset metric counters
        inscriptioncount = 0
        newinscriptioncount = 0
        removefilecount = 0
        mempoolItem = 0

        # report mempool opening state
        mempoolLength = len(self.mempool)
        self.log(f"current mempool transaction count: {mempoolLength}")

        # get existing filenames
        self.log(f"checking files vs mempool")
        insnotinpool = list(set(self.inscriptions) - set(self.mempool))
        if len(insnotinpool) > 0:
            self.log(f"looking to remove {len(insnotinpool)} transactions")
        # assuming listdir is faster then globbing each file because we dont know the file extension from txid
        dirlist = os.listdir(self.inscriptionMempoolDir)
        for fn in dirlist:
            if not fn.startswith("inscription-"): continue
            fntx = fn.split("-")[1]
            if fntx.find(".") > -1: fntx = fntx.split(".")[0]
            if fntx not in self.mempool:
                os.remove(f"{self.inscriptionMempoolDir}{fn}")
                if fntx in self.inscriptions:
                    self.inscriptions.remove(fntx)
                removefilecount += 1
        self.log(f"removed {removefilecount} files for inscriptions no longer in mempool")

        # not inscriptions setup
        nlb = len(self.notInscriptions)
        self.log(f"checking {nlb} prior tx known not to be inscriptions vs mempool")
        self.notInscriptions = list(set(self.mempool) & set(self.notInscriptions))
        with open(f"{self.inscriptionMempoolDir}/data-notinscriptions.json", "w") as f:
            json.dump(self.notInscriptions, f)
        nl = len(self.notInscriptions)
        self.log(f"after purge, the number of tx that are not inscriptions is {nl} (was {nlb})")
        self.mempool = list(set(self.mempool) - set(self.notInscriptions))

        # check tx in mempool
        checkTimeAllowed = self.interval // 2
        checkTimeStart = int(time.time())
        nml = len(self.mempool)
        self.log(f"checking {nml} remaining tx in mempool for inscriptions")
        for txid in self.mempool:
            processtx = True
            mempoolItem += 1
            # check if not an inscription
            if txid in self.notInscriptions:
                processtx = False

            # check if file already extracted - there can be multiple extracted per tx
            # baseFileName = self._getBaseFilenameForTXID(txid)
            # for fm in glob.glob(f"{baseFileName}*"):
            #     processtx = False
            #     inscriptioncount += 1
            if txid in self.inscriptions:
                processtx = False
                inscriptioncount += 1
            
            if processtx:
                inscriptionsExtractedFromTX = self._extractTX(txid)
                inscriptioncount += inscriptionsExtractedFromTX
                newinscriptioncount += inscriptionsExtractedFromTX
            # eye candy every 500 tx, and intermediate save every 5000
            if (mempoolItem % 500) == 0:
                if (mempoolItem % 5000) != 0:
                    self.log(f"processed {mempoolItem} transactions so far ({inscriptioncount} inscriptions found)")
                else:
                    self.log(f"processed {mempoolItem} of {mempoolLength} transactions so far")
                    with open(f"{self.inscriptionMempoolDir}/data-notinscriptions.json", "w") as f:
                        json.dump(self.notInscriptions, f)
                    with open(f"{self.inscriptionMempoolDir}/data-inscriptions.json", "w") as f:
                        json.dump(self.inscriptions, f)
                checkTimeCurrent = int(time.time())
                # bail if this is taking too long due to size of mempool
                if checkTimeCurrent - checkTimeStart >= checkTimeAllowed:
                    self.log(f"not checking any more transactions as time expired")
                    break

        # summary and save our known state
        self.log(f"done this pass through mempool.")
        self.log(f"inscriptions found: {inscriptioncount} ({newinscriptioncount} new) from {mempoolLength} mempool tx")
        with open(f"{self.inscriptionMempoolDir}/data-notinscriptions.json", "w") as f:
            json.dump(self.notInscriptions, f)
        with open(f"{self.inscriptionMempoolDir}/data-inscriptions.json", "w") as f:
            json.dump(self.inscriptions, f)


        # Generate image of recent files extracted
        # Set relative area sizes so that we create a 3x5 layout of images
        self.headerHeight = int(self.height * 20 / 320)
        super().startImage()
        availHeight = self.getInsetHeight()
        col, row = 0, 0
        filelist = self._getMostRecentImages(25)
        tileSideAdj = 72
        tileSideAdj = 96 if len(filelist) < 18 else tileSideAdj
        tileSideAdj = 144 if len(filelist) < 10 else tileSideAdj
        tileSide = int(self.height * tileSideAdj / 320)
        colMax = int(self.width/tileSide)
        rowMax = int(availHeight/tileSide)
        padleft = (self.width - (colMax*tileSide)) // 2
        for filename in filelist:
            if row >= rowMax:
                break
            x = int(padleft + (col*tileSide))
            y = int(self.getInsetTop() + (row*tileSide))
            fileext = filename.rpartition('.')[2]
            try:
                img = vicariousnetwork.getimagefromfile("file://" + filename)
                img.thumbnail((tileSide,tileSide))
                img = img.resize((tileSide,tileSide),Image.Resampling.NEAREST) # scales up small images to fit
                x += (tileSide - img.width)//2
                y += (tileSide - img.height)//2
                self.canvas.paste(img, box=(x,y))
                img.close()
                # next tile position
                col = col + 1 if col < colMax-1 else 0
                row = row + 1 if col == 0 else row
            except Exception as e:
                self.log(f"error processing image: {e}")
        super().finishImage()


# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = InscriptionMempoolPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            arg0 = sys.argv[0]
            print(f"Produces image with Unmined Inscriptions")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configured defaults")
            print(f"2) Pass the desired width and height as an argument as follows")
            print(f"   {arg0} 1920 1080")
        else:
            if len(sys.argv) > 2:
                p.width = int(sys.argv[1])
                p.height = int(sys.argv[2])
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()