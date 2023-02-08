#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor, ImageFile
from io import BytesIO
from wand.api import library
import glob
import exifread
import json
import locale
import logging
import math
import os
import numpy
import random
import re
import subprocess
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext
import vicariouswatermark
import wand.color
import wand.image


def getmostrecent(max):
    files = list(filter(os.path.isfile, glob.glob(ordinalsDirectory + "inscription*")))
    files.sort(key=os.path.getctime)
    limitedlist = files[max*-1:]
    reversedlist = limitedlist[::-1]
    return reversedlist

def createimage(width=480,height=320):
    canvas = Image.new(mode="RGBA", size=(width,height), color=colorBackground)
    draw = ImageDraw.Draw(canvas)
    padtop = 20
    footersize = 12
    availheight = height - (padtop+footersize)
    col = 0
    row = 0
    imagewidth = 96
    colmax = int(width/imagewidth)          # 8
    rowmax = int(availheight/imagewidth)    # 6
    w = imagewidth #  int(width/colmax)
    h = imagewidth #int(height/colmax)
    padleft = int((width - (colmax*imagewidth)) / 2)
    filelist = getmostrecent(colmax * rowmax)
    for filename in filelist:
        if row >= rowmax:
            break
        x = int(padleft + (col*w))
        y = int(padtop + (row*h))
        fileext = filename.rpartition('.')[2]
        if fileext in ['bmp','gif','jpg','png','svg','tiff','webp']:
            try:
                img = vicariousnetwork.getimagefromfile("file://" + filename)
                img.thumbnail((w,h))
                x += int((w - img.width)/2)
                y += int((h - img.height)/2)
                canvas.paste(img, box=(x,y))
                img.close()
            except Exception as e:
                print(f"error processing image: {e}")
                vicarioustext.drawcenteredtext(draw, fileext.upper(), 14, x + int(w//2), y + int(h//2), colorTextFG, True)
        else:
            vicarioustext.drawcenteredtext(draw, fileext.upper(), 14, x + int(w//2), y + int(h//2), colorTextFG, True)
        # next tile position
        col = col + 1 if col < colmax-1 else 0
        row = row + 1 if col == 0 else row
    # header
    vicarioustext.drawcenteredtext(draw, "Recent Unmined Inscriptions In Mempool", 20, int(width/2), int(padtop/2), colorTextFG, True)
    # footer
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # watermark
    vicariouswatermark.do(canvas,width=99,box=(0,height-12))
    # save it
    canvas.save(outputFile)
    canvas.close()


def getordinalfortx(txid):
    ordinals = []
    tx = vicariousbitcoin.gettransaction(txid)
    thepattern = re.compile("(.*)0063036f72640101(.*)68$")  # OP_FALSE OP_IF push-3-bytes 'ord' push-1-byte 1
    txidx = -1
    if True:
        if True:
            txsize = tx["size"]
            vinidx = 0
            if "vin" in tx:
                for vin in tx["vin"]:
                    vinidx += 1
                    if "txinwitness" in vin:
                        for txinwitness in vin["txinwitness"]:
                            match = re.match(thepattern, txinwitness)
                            if match is not None:
                                # This is an ordinal inscription.
                                # Get parent info
                                parenttxid = ""
                                parentsize = 0
                                if "txid" in vin:
                                    parenttxid = vin["txid"]
                                    parentsize = vicariousbitcoin.gettransaction(parenttxid)["size"]
                                #print(f"found ordinal in tx idx:{txidx} of block {blocknum}")
                                g2 = match.group(2)
                                pos = 0
                                contenttypelength = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                                pos += 2
                                contenttype = bytes.fromhex(g2[pos:pos+(contenttypelength*2)]).decode()
                                pos += (contenttypelength*2)
                                opcode = g2[pos:pos+2]
                                pos += 2
                                if opcode != '00':
                                    print(f"warning. expected 0x00 divider between content type and data, but got 0x{opcode}")
                                #print(f"- content type: {contenttype}")
                                datalengthtype = g2[pos:pos+2]
                                pos +=2
                                datalen = 0
                                totaldatalen = 0
                                rawbytes = bytearray()
                                while datalengthtype in ['4c','4d','4e']:
                                    #print(f"- hex code for data length: {datalengthtype}")
                                    # size was reporting 2050, which is 802 in hex. flip the endian, 208 = 520, the max bytes that can be pushed
                                    if datalengthtype == "4c":
                                        # next 1 byte for size
                                        datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                                        pos += 2
                                    if datalengthtype == "4d":
                                        # next 2 bytes for size
                                        datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+4]),"little")
                                        pos += 4
                                    if datalengthtype == "43":
                                        # next 4 bytes for size
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
                                #print(f"pos: {pos}, totaldatalen: {totaldatalen}, remaining: {remaininghex}, remaininghexlength: {remaininghexlength}")
                                if remaininghexlength > 0:
                                    morebytes = bytes.fromhex(g2[pos:])
                                    rawbytes.extend(morebytes)
                                    totaldatalen += (remaininghexlength/2)
                                #print(f"- total data length: {totaldatalen}")
                                # append an object
                                ordinal = {"block":-1,"txid":txid,"txsize":txsize,"txidx":txidx,"contenttype":contenttype,"size":totaldatalen,"parenttxid":parenttxid,"parentsize":parentsize,"data":rawbytes}
                                ordinals.append(ordinal)
    return ordinals


femap = {
    "application/hta": "hta",
    "application/msword": "doc",
    "application/octet-stream": "bin",
    "application/pdf": "pdf",
    "application/pgp-signature": "sig",
    "application/postscript": "ps",
    "application/rtf": "rtf",
    "application/vnd.ms-excel": "xls",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.ms-project": "mpp",
    "application/x-javascript": "js",
    "application/x-msaccess": "mdb",
    "application/x-tar": "tar",
    "application/zip": "zip",
    "audio/flac": "flac",
    "audio/midi": "midi",
    "audio/mpeg": "mp3",
    "audio/x-wav": "wav",
    "image/avif": "avif",
    "image/bmp": "bmp",
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/svg": "svg",
    "image/svg+xml": "svg",
    "image/tiff": "tiff",
    "image/webp": "webp",
    "image/x-icon": "ico",
    "image/x-xbitmap": "xbm",
    "text/css": "css",
    "text/htm": "htm",
    "text/html": "html",
    "text/plain": "txt",
    "text/richtext": "rtx",
    "video/mp4": "mp4",
    "video/mpeg": "mpeg",
    "video/webm": "webm",
    "video/quicktime": "qt",
    "x-word/x-vrml": "vrml",
}

def getfileextensionfromcontenttype(ct):
    r = "bin"
    mt = ct.split(";")[0]
    if mt in femap:
        r = femap[mt]
    return r

def getbasefilenamefortxid(txid):
    global ordinalsDirectory
    filename = ordinalsDirectory + "inscription-"+txid
    return filename

def extracttx(txid="00"):
    global notinscriptions
    global inscriptions
    global inscriptioncount
    global newinscriptioncount
    global inscriptiontxsize
    ordinals = getordinalfortx(txid)
    ordcount = len(ordinals)
    if ordcount == 0:
        notinscriptions.append(txid)
        return

    ordcount = 0
    for ordinal in ordinals:
        ordcount += 1
        txidx =  int(ordinal["txidx"]) if "txidx" in ordinal else -1
        handled = False
        size = 0
        contenttype = "undefined"
        try:
            size = int(ordinal["size"]) if "size" in ordinal else 0
            txsize = ordinal["txsize"]
            parentsize = ordinal["parentsize"]
            totalsize = txsize + parentsize
            contenttype = ordinal["contenttype"] if "contenttype" in ordinal else "undefined"
            fileextension = getfileextensionfromcontenttype(contenttype)
            exportFileName = getbasefilenamefortxid(txid) + "." + fileextension
            exportFolder = exportFileName.rpartition('/')[0]
            if not os.path.exists(exportFolder):
                os.makedirs(exportFolder)
            print(f"- exporting file to {exportFileName}")
            bytesioblob = BytesIO(ordinal["data"])
            with open(exportFileName, "wb") as f:
                f.write(bytesioblob.getbuffer())
        except Exception as e:
            print(f"Error processing ordinal: {e}")
            print(f"txid: {txid}, size: {size} for content-type: {contenttype}")
    inscriptions.append(txid)
    inscriptioncount += ordcount
    newinscriptioncount += ordcount
    inscriptiontxsize += totalsize

def loadset(k):
    fn = ordinalsDirectory + "data-" + k + ".json"
    if os.path.exists(fn):
        with open(fn, "r") as f:
            return json.load(f)
    return []

def saveset(k, s):
    fn = ordinalsDirectory + "data-" + k + ".json"
    with open(fn, "w") as f:
        json.dump(s, f)

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/inscriptionmempool.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/inscriptionmempool.png"
    dataDirectory="/home/nodeyez/nodeyez/data/"
    width=480
    height=320
    sleepInterval = 10
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    # Initializations
    ImageFile.LOAD_TRUNCATED_IMAGES=True
    outsetkey = "notinscriptions"
    notinscriptions = []
    insetkey = "inscriptions"
    inscriptions = []
    runonce=False
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "inscriptionmempool" in config:
            config = config["inscriptionmempool"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 10 if sleepInterval < 10 else sleepInterval # all local, but no need to be overly aggressive
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    ordinalsDirectory = dataDirectory + "inscription-mempool/"
    if not os.path.exists(ordinalsDirectory):
        os.makedirs(ordinalsDirectory)
    # Check args
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help'] or len(sys.argv) != 3:
            print(f"Produces image with Unmined Inscriptions")
            print(f"Usage:")
            print(f"1) Pass the desired width and height as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} 1920 1080")
            exit(0)
        if len(sys.argv) > 2:
            width = int(sys.argv[1])
            height = int(sys.argv[2])
            runonce = True

    # load json files
    notinscriptions = loadset(outsetkey)
    inscriptions = loadset(insetkey)

    # continuous
    while True:
        # reset metric counters
        inscriptioncount = 0
        newinscriptioncount = 0
        inscriptiontxsize = 0

        # get mempool
        print(f"--- Checking mempool ---")
        print(f"date and time: {vicarioustext.getdateandtime()}")
        mempool = vicariousbitcoin.getmempool()
        mc = 0
        ml = len(mempool)
        print(f"transaction count: {ml}")

        # get existing filenames
        print(f"checking files vs mempool")
        insnotinpool = list(set(inscriptions) - set(mempool))
        if len(insnotinpool) > 0:
            print(f"looking to remove {len(insnotinpool)} transactions")
        # assuming listdir is faster then globbing each file because we dont know the file extension from txid
        dirlist = os.listdir(ordinalsDirectory)
        removefilecount = 0
        for fn in dirlist:
            if fn.startswith("inscription-" + insetkey):
                continue
            if fn.startswith("inscription-" + outsetkey):
                continue
            fntx = fn.split("-")[1].split(".")[0]
            if fntx not in mempool:
                # print(f"removing file {fn} as txid no longer in mempool")
                fp = ordinalsDirectory + fn
                os.remove(fp)
                if fntx in inscriptions:
                    inscriptions.remove(fntx)
                removefilecount += 1
        if removefilecount > 0:
            print(f"removed {removefilecount} files that are no longer in mempool") # ideally same as len(isnotinpool)

        # not inscriptions setup
        print(f"checking prior tx known not to be inscriptions vs mempool")
        nlb = len(notinscriptions)
        notinscriptions = list(set(mempool) & set(notinscriptions))
        saveset(outsetkey, notinscriptions)
        nl = len(notinscriptions)
        print(f"The non-inscription length after purge: {nl}, was {nlb}")
        mempool = list(set(mempool) - set(notinscriptions))
        nml = len(mempool)
        print(f"will check {nml} remaining tx in mempool for inscriptions")

        # check tx in mempool
        for txid in mempool:
            processtx = True
            mc = mc + 1
            # check if not an ordinal
            if txid in notinscriptions:
                processtx = False
            # check if file already extracted - seems inefficient. could use the inscriptions set
            for fm in glob.glob(getbasefilenamefortxid(txid) + "*"):
                processtx = False
                inscriptioncount += 1
                fsize = os.path.getsize(fm) # because of this we need actual file so had to glob
                inscriptiontxsize += fsize
            if processtx:
                extracttx(txid)
            # eye candy every 500 tx
            if (mc % 500) == 0:
                print(f"processed {mc}")
            # save every 5000 tx
            if (mc % 5000) == 0:
                print(f"  of {ml}")
                # save sets
                saveset(outsetkey, notinscriptions)
                saveset(insetkey, inscriptions)

        print(f"Done this pass through mempool.")
        print(f"Inscriptions found: {inscriptioncount} ({newinscriptioncount} new) from {ml} mempool tx. Inscriptions using {inscriptiontxsize} bytes in mempool")
        # save sets
        saveset(outsetkey, notinscriptions)
        saveset(insetkey, inscriptions)
        # list the newest files -- will create display panel of these
        createimage(width, height)

        if runonce:
            break

        print(f"sleeping for {sleepInterval}")
        time.sleep(sleepInterval)

