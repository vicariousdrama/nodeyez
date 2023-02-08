#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor, ImageFile
from io import BytesIO
from wand.api import library
import exifread
import json
import locale
import logging
import math
import os
import numpy
import random
import subprocess
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext
import vicariouswatermark
import wand.color
import wand.image

def getmaxtextforwidth(draw, words, width, fontsize, isbold=False):
    wlen = len(words)
    if wlen == 0:
        return "", []
    for x in range(wlen, 0, -1):
        s = " ".join(words[0:x])
        sw,sh,f = vicarioustext.gettextdimensions(draw, s, fontsize, isbold)
        if sw <= width:
            return s, words[x:]

def resizeToWidth(imInput, desiredWidth):
    w = imInput.width
    h = imInput.height
    if w == desiredWidth:
        return imInput
    else:
        r = desiredWidth / w
        nw = int(w * r)
        nh = int(h * r)
        imOutput = imInput.resize((nw,nh))
        return imOutput

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

def createimage(blocknumber=1, width=480, height=320):
    global blocklistChecktime
    global blocklistActive
    global blocklistHeight
    global blocklistDefinitions

    # blocklist filter prep
    blockIndexesToSkip = []
    if len(blocklistURL) > 0 and time.time() > blocklistChecktime + 21600: #6 hours
        blocklistActive, blocklistHeight, blocklistDefinitions = getblocklist(blocklistURL)
        blocklistChecktime = time.time()
    if blocklistActive:
        if int(blocklistHeight) < int(blocknumber):
            print(f"A blocklist is configured and block height {blocknumber} is higher then vetted block height {blh}. Skipping.")
            return
        for blocklistDefinition in blocklistDefinitions:
            dBlock = int(blocklistDefinition["blocknumber"])
            if dBlock == int(blocknumber):
                blockIndexesToSkip.append(int(blocklistDefinition["idx"]))


    ordinals = vicariousbitcoin.getblockordinals(blocknumber, blockIndexesToSkip)
    ordcount = len(ordinals)
    if ordcount == 0:
        print(f"No ordinals found in block {blocknumber}")
        return
    print(f"Found {ordcount} ordinals in block {blocknumber}.")
    bn=f'{blocknumber:,}'.replace(',','/')
    bn=bn.rpartition('/')[0]+"/"+str(blocknumber)

    ordcount = 0
    for ordinal in ordinals:
        ordcount += 1
        txidx =  int(ordinal["txidx"]) if "txidx" in ordinal else -1
        print(f"Processing ordinal {ordcount} in index {txidx}")
        handled = False
        size = 0
        contenttype = "undefined"
        try:
            if txidx in blockIndexesToSkip:
                reportAsBlockedInLog = False
                if reportAsBlockedInLog:
                    raise Exception("Blocked")
                continue
            size = int(ordinal["size"]) if "size" in ordinal else 0
            txsize = ordinal["txsize"]
            parentsize = ordinal["parentsize"]
            totalsize = txsize + parentsize
            sizestr = f"data size: {size}, tx size: {txsize}, commitment tx size: {parentsize}, total size: {totalsize}"
            contenttype = ordinal["contenttype"] if "contenttype" in ordinal else "undefined"
            if contenttype in ["image/gif","image/jpeg","image/png","image/svg","image/svg+xml","image/webp"]:
                canvas = Image.new(mode="RGBA", size=(width,height), color=colorBackground)
                draw = ImageDraw.Draw(canvas)
                padtop=40
                exif = {}
                # Load ordinal image
                img=Image.new(mode="RGB",size=(1,1),color=ImageColor.getrgb("#7f007f")) # default if not loaded from type
                if contenttype in ["image/gif", "image/jpeg", "image/png", "image/webp"]:
                    img = Image.open(BytesIO(ordinal["data"])).convert('RGBA')
                    tags = exifread.process_file(BytesIO(ordinal["data"]), details=False)
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
                if contenttype in ["image/svg", "image/svg+xml"]:
                    with wand.image.Image() as image:
                        image.read(blob=BytesIO(ordinal["data"]),format="svg")
                        img = Image.open(BytesIO(image.make_blob("png32")))

                # Resize to fit
                img = resizeToWidth(img, width)
                irw = float(img.height)/float(img.width)
                irh = float(img.width)/float(img.height)
                cpb = canvas.height - padtop - 20
                if img.height > cpb:
                    img = img.resize((int(cpb*irh),cpb))
                # Paste it
                xpos = int((canvas.width - img.width)/2)
                canvas.paste(img, box=(xpos,padtop))
                img.close()
                # Header label
                vicarioustext.drawcenteredtext(draw, "Ordinal Inscription in " + str(blocknumber), 24, int(width/2),int(padtop/2), colorTextFG, True)
                # Overlay
                if overlayTextEnabled:
                    overlayimg = Image.new(mode="RGBA", size=(width,height), color=(0,0,0,0))
                    overlaydraw = ImageDraw.Draw(overlayimg)
                    otw,oth,otf = vicarioustext.gettextdimensions(draw, "txid: " + ordinal["txid"], 10)
                    oth = 36 + (12 * len(exif)) if overlayExifEnabled else 36
                    overlaydraw.rectangle(xy=((width-otw,height-oth),(width,height)),fill=overlayTextColorBG)
                    if overlayExifEnabled:
                        exifidx = 0
                        for k in exif:
                            exifidx += 1
                            vicarioustext.drawbottomrighttext(overlaydraw, k + ": " + str(exif[k]), 10, width, height-24-(exifidx*12), overlayTextColorFG)
                    vicarioustext.drawbottomrighttext(overlaydraw, "content-type: " + contenttype, 10, width, height-24, overlayTextColorFG)
                    vicarioustext.drawbottomrighttext(overlaydraw, sizestr, 10, width, height-12, overlayTextColorFG)
                    vicarioustext.drawbottomrighttext(overlaydraw, ordinal["txid"], 9, width, height, overlayTextColorFG)
                    canvas.alpha_composite(overlayimg)
                    overlayimg.close()
                else:
                    # Footer line without overlay background
                    vicarioustext.drawbottomrighttext(draw, "txid: " + ordinal["txid"], 10, width, height, colorTextFG)
                # Watermark
                vicariouswatermark.do(canvas,width=99,box=(0,height-12))
                # Save each unique name
                if saveUniqueImageNames:
                    ordoutputFile = uniqueOutputFile.replace(".png","-"+bn+"-"+str(ordinal["txidx"])+".png")
                    ordoutputFolder = ordoutputFile.rpartition('/')[0]
                    if not os.path.exists(ordoutputFolder):
                        os.makedirs(ordoutputFolder)
                    canvas.save(ordoutputFile)
                # Save the single name
                canvas.save(outputFile)
                canvas.close()
                handled = True
#            elif contenttype.startswith("text/"):
#                print(f"Ordinal is text. Here is the contents\n")
#                print(ordinal["data"].decode())
#                handled = True
            if not handled:
                print(f"- no handler yet for content-type: {contenttype}")
                print(f"- {sizestr}")
            if exportFilesToDataDirectory:
                fileextension = getfileextensionfromcontenttype(contenttype)
                exportFileName = ordinalsDirectory + "inscription-"+bn+"-" + str(ordinal["txidx"]) + "." + fileextension
                exportFolder = exportFileName.rpartition('/')[0]
                if not os.path.exists(exportFolder):
                    os.makedirs(exportFolder)
                print(f"- exporting file to {exportFileName}")
                bytesioblob = BytesIO(ordinal["data"])
                with open(exportFileName, "wb") as f:
                    f.write(bytesioblob.getbuffer())

        except Exception as e:
            print(f"Error processing ordinal: {e}")
            print(f"Size was {size} for content-type: {contenttype}")

def getblocklist(u):
    h = -1
    b = []
    if len(u) > 0:
        j = vicariousnetwork.geturl(useTor, u, '{"vettedheight":-1,"blocklist":[]}', headers={})
        b = j["blocklist"]
        h = j["vettedheight"]
    return (h > -1), h, b


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/ordinals.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/ordinals.png"
    uniqueOutputFile="/home/nodeyez/nodeyez/imageoutput/ordinals/ordinals.png"
    dataDirectory="/home/nodeyez/nodeyez/data/"
    exportFilesToDataDirectory=True
    saveUniqueImageNames=True
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=30
    ImageFile.LOAD_TRUNCATED_IMAGES=True
    overlayTextEnabled=True
    overlayExifEnabled=True
    overlayTextColorBG=ImageColor.getrgb("#00000040")
    overlayTextColorFG=ImageColor.getrgb("#ffffffff")
    blocklistURL=""
    blocklistChecktime=0
    blocklistActive=False
    blocklistHeight=-1
    blocklistDefinitions=[]
    useTor=True
    logging.getLogger("exifread").setLevel(logging.ERROR)
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "ordinals" in config:
            config = config["ordinals"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "uniqueOutputFile" in config:
            uniqueOutputFile = config["uniqueOutputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "exportFilesToDataDirectory" in config:
            exportFilesToDataDirectory = config["exportFilesToDataDirectory"]
        if "saveUniqueImageNames" in config:
            saveUniqueImageNames = config["saveUniqueImageNames"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, local only
        if "overlayTextEnabled" in config:
            overlayTextEnabled = config["overlayTextEnabled"]
        if "overlayExifEnabled" in config:
            overlayExifEnabled = config["overlayExifEnabled"]
        if "overlayTextColorBG" in config:
            overlayTextColorBG = ImageColor.getrgb(config["overlayTextColorBG"])
        if "overlayTextColorFG" in config:
            overlayTextColorFG = ImageColor.getrgb(config["overlayTextColorFG"])
        if "blocklistURL" in config:
            blocklistURL = config["blocklistURL"]
        if "useTor" in config:
            useTor = config["useTor"]
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    ordinalsDirectory = dataDirectory + "ordinals/"
    if not os.path.exists(ordinalsDirectory):
        os.makedirs(ordinalsDirectory)
    if saveUniqueImageNames:
        uniqueImageDirectory = uniqueOutputFile[0:uniqueOutputFile.rindex("/")] + "/"
        if not os.path.exists(uniqueImageDirectory):
            os.makedirs(uniqueImageDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces image(s) with Ordinal Inscription data")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired block number or range as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} 767430")
            print(f"   {arg0} 767430-774999")
            print(f"3) Pass the desired block number or range, width and height as arguments")
            print(f"   {arg0} 775100 1920 1080")
            print(f"   {arg0} 774000-774999 1920 1080")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
        blocknumbers = sys.argv[1].split('-')
        blocknumber = int(blocknumbers[0])
        blocknumberend = int(blocknumbers[1]) if len(blocknumbers) > 1 else blocknumber
        if len(sys.argv) > 3:
            width = int(sys.argv[2])
            height = int(sys.argv[3])
        while blocknumber <= blocknumberend:
            createimage(blocknumber,width,height)
            blocknumber += 1
        exit(0)
    # Loop
    oldblocknumber = 0
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        if oldblocknumber != blocknumber:
            blocknumber = oldblocknumber + 1 if oldblocknumber != 0 else blocknumber # force it to next, dont skip any blocks
            createimage(blocknumber,width,height)
            oldblocknumber = blocknumber
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
