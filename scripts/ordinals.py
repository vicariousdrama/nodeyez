#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
from io import BytesIO
import json
import locale
import math
import numpy
import random
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext

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

def createimage(blocknumber=1, width=480, height=320):
    ordinals = vicariousbitcoin.getblockordinals(blocknumber)
    ordcount = len(ordinals)
    if ordcount == 0:
        print(f"No ordinals found in block {blocknumber}")
        return
    print(f"Found {ordcount} ordinals in block {blocknumber}.")

    ordcount = 0
    for ordinal in ordinals:
        ordcount += 1
        print(f"Processing ordinal {ordcount}")
        try:
            if ordinal["contenttype"] in ["image/png","image/jpeg"]:
                print(f"Ordinal is an image. Will try to load to render it")
                canvas = Image.new(mode="RGB", size=(width,height), color=colorBackground)
                draw = ImageDraw.Draw(canvas)
                padtop=40
                # Load ordinal image
                img = Image.open(BytesIO(ordinal["data"]))
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
                # TODO: Any additional metadata can be overlayed like was done with raretoshi
                # Header label
                vicarioustext.drawcenteredtext(draw, "Ordinal Inscription in " + str(blocknumber), 24, int(width/2),int(padtop/2), colorTextFG, True)
                # Footer
                vicarioustext.drawbottomrighttext(draw, "txid:" + ordinal["txid"], 10, width, height)
                # Save it
                ordoutputFile = outputFile.replace(".png","-"+str(blocknumber)+"-"+str(ordinal["txidx"])+".png")
                print(f"Saving image as {ordoutputFile}")
                canvas.save(ordoutputFile)
                canvas.close()
            if ordinal["contenttype"].startswith("text/"):
                print(f"Ordinal is text. Here is the contents\n")
                print(ordinal["data"].decode())
        except Exception as e:
            print(f"Error processing ordinal: {e}")



if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/ordinals.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/ordinals.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=30
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "ordinals" in config:
            config = config["ordinals"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
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
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces image(s) with Ordinal Inscription data")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired block number as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} 722231")
            print(f"3) Pass the desired block number, width and height as arguments")
            print(f"   {arg0} 722231 1920 1080")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
        blocknumber = int(sys.argv[1])
        if len(sys.argv) > 3:
            width = int(sys.argv[2])
            height = int(sys.argv[3])
        createimage(blocknumber,width,height)
        exit(0)
    # Loop
    oldblocknumber = 0
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        if oldblocknumber != blocknumber:
            createimage(blocknumber,width,height)
            oldblocknumber = blocknumber
        #print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
